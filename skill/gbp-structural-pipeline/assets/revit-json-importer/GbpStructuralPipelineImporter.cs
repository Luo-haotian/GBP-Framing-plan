using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Web.Script.Serialization;
using System.Windows.Forms;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;

namespace GbpStructuralPipeline.Revit2023
{
    [Transaction(TransactionMode.Manual)]
    public class ImportNeutralJsonCommand : IExternalCommand
    {
        private const string ParamName = "GBP_JSON_ID";
        private const string ParamRole = "GBP_STRUCTURAL_ROLE";
        private const string ParamSection = "GBP_SECTION";
        private const string ParamStatus = "GBP_MODEL_STATUS";
        private const string ParamSource = "GBP_SOURCE";
        private const string AppId = "GBP_STRUCTURAL_PIPELINE";
        private const double MmToFeet = 1.0 / 304.8;

        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            UIDocument uidoc = commandData.Application.ActiveUIDocument;
            if (uidoc == null || uidoc.Document == null)
            {
                message = "Open a Revit project before importing neutral JSON.";
                return Result.Failed;
            }

            string jsonPath = PickJsonFile();
            if (string.IsNullOrEmpty(jsonPath))
            {
                return Result.Cancelled;
            }

            try
            {
                Dictionary<string, object> model = ReadJson(jsonPath);
                ImportModel(commandData.Application.Application, uidoc.Document, model);
                TaskDialog.Show("GBP Structural Pipeline", "Import complete.\n\nSource:\n" + jsonPath);
                return Result.Succeeded;
            }
            catch (Exception ex)
            {
                message = ex.ToString();
                TaskDialog.Show("GBP Structural Pipeline Import Error", ex.Message);
                return Result.Failed;
            }
        }

        private static string PickJsonFile()
        {
            OpenFileDialog dialog = new OpenFileDialog();
            dialog.Title = "Select neutral_structural_model JSON";
            dialog.Filter = "JSON files (*.json)|*.json|All files (*.*)|*.*";
            dialog.CheckFileExists = true;
            dialog.Multiselect = false;
            return dialog.ShowDialog() == DialogResult.OK ? dialog.FileName : null;
        }

        private static Dictionary<string, object> ReadJson(string path)
        {
            JavaScriptSerializer serializer = new JavaScriptSerializer();
            serializer.MaxJsonLength = int.MaxValue;
            object value = serializer.DeserializeObject(File.ReadAllText(path));
            return Obj(value);
        }

        private static void ImportModel(Autodesk.Revit.ApplicationServices.Application app, Document doc, Dictionary<string, object> model)
        {
            Dictionary<string, object> intent = Obj(model["intent_model"]);
            Dictionary<string, object> seed = Obj(model["analysis_seed_model"]);
            int importElementCount = EstimateImportElementCount(intent);
            if (importElementCount > 1200)
            {
                throw new InvalidOperationException("This JSON contains " + importElementCount + " importable review elements. Use a standard-floor compact model for Revit review, or split the import by floor group. This guard prevents Revit from hanging on fully expanded repeated floors. Current v0.16 review models are expected to stay below 1200 elements.");
            }
            Dictionary<string, object> sectionLookup = BuildLookup(Arr(seed["sections"]));
            Dictionary<string, object> levelLookup = BuildLookup(Arr(intent["levels"]));

            using (Transaction tx = new Transaction(doc, "Import GBP neutral structural JSON"))
            {
                tx.Start();
                EnsureJsonIdParameter(app, doc);

                ImportLevels(doc, Arr(intent["levels"]));
                ImportStructuralPlanViews(doc, Arr(intent["levels"]));
                ImportGrids(doc, Arr(intent["grids"]));
                ImportColumns(doc, Arr(intent["columns"]), levelLookup, sectionLookup);
                ImportWalls(doc, Arr(intent["walls"]), levelLookup);
                ImportBeams(doc, Arr(intent["beams"]), levelLookup, sectionLookup);
                ImportSlabs(doc, Arr(intent["slabs"]), levelLookup);
                ImportOpenings(doc, Arr(intent["openings"]), levelLookup);
                ImportReviewNotes(doc, intent, sectionLookup, levelLookup);

                tx.Commit();
            }
        }

        private static void ImportLevels(Document doc, IList levels)
        {
            foreach (object item in levels)
            {
                Dictionary<string, object> level = Obj(item);
                string id = Str(level, "id");
                string name = Str(level, "name", id);
                double elevation = Feet(Num(level, "elevation"));

                Element existing = FindByJsonId(doc, id);
                Level revitLevel = existing as Level;
                if (revitLevel == null)
                {
                    revitLevel = FindLevelByName(doc, name);
                }
                if (revitLevel == null)
                {
                    revitLevel = Level.Create(doc, elevation);
                }
                SafeSetName(revitLevel, name);
                Stamp(revitLevel, id, "level");
            }
        }

        private static int EstimateImportElementCount(Dictionary<string, object> intent)
        {
            int count = 0;
            foreach (string key in new[] { "levels", "grids", "columns", "walls", "beams", "slabs", "openings" })
            {
                if (intent.ContainsKey(key))
                {
                    count += Arr(intent[key]).Count;
                }
            }
            return count;
        }

        private static void ImportGrids(Document doc, IList grids)
        {
            foreach (object item in grids)
            {
                Dictionary<string, object> grid = Obj(item);
                string id = Str(grid, "id");
                DeleteExistingByJsonId(doc, id);
                IList curve = Arr(grid["curve"]);
                if (curve.Count < 2)
                {
                    continue;
                }
                XYZ p0 = Point2(Obj(curve[0]), 0);
                XYZ p1 = Point2(Obj(curve[curve.Count - 1]), 0);
                if (p0.DistanceTo(p1) < 0.001)
                {
                    continue;
                }
                Grid revitGrid = Grid.Create(doc, Line.CreateBound(p0, p1));
                SafeSetName(revitGrid, Str(grid, "label", id));
                Stamp(revitGrid, id, "grid");
            }
        }

        private static void ImportColumns(Document doc, IList columns, Dictionary<string, object> levelLookup, Dictionary<string, object> sectionLookup)
        {
            foreach (object item in columns)
            {
                Dictionary<string, object> column = Obj(item);
                string id = Str(column, "id");
                DeleteExistingByJsonId(doc, id);
                Dictionary<string, object> baseLevel = Obj(levelLookup[Str(column, "base_level_id")]);
                Dictionary<string, object> topLevel = Obj(levelLookup[Str(column, "top_level_id")]);
                double z0 = Feet(Num(baseLevel, "elevation"));
                double z1 = Feet(Num(topLevel, "elevation"));
                Dictionary<string, object> location = Obj(column["location"]);
                Dictionary<string, object> section = GetSection(sectionLookup, Str(column, "section_seed_id"));
                Dictionary<string, object> geom = section.ContainsKey("geometry") ? Obj(section["geometry"]) : new Dictionary<string, object>();
                double b = Feet(Num(geom, "b_mm", 600));
                double h = Feet(Num(geom, "h_mm", 600));
                double x = Feet(Num(location, "x"));
                double y = Feet(Num(location, "y"));
                IList<XYZ> footprint = Rectangle(x, y, b, h, Math.Min(z0, z1));
                string label = id + " " + SectionLabel(section);
                DirectShape ds = CreateExtrudedShape(doc, BuiltInCategory.OST_StructuralColumns, label, footprint, Math.Abs(z1 - z0));
                Stamp(ds, id, "column", SectionLabel(section));
            }
        }

        private static void ImportWalls(Document doc, IList walls, Dictionary<string, object> levelLookup)
        {
            foreach (object item in walls)
            {
                Dictionary<string, object> wall = Obj(item);
                string id = Str(wall, "id");
                DeleteExistingByJsonId(doc, id);
                Dictionary<string, object> baseLevel = Obj(levelLookup[Str(wall, "base_level_id")]);
                Dictionary<string, object> topLevel = Obj(levelLookup[Str(wall, "top_level_id")]);
                double z0 = Feet(Num(baseLevel, "elevation"));
                double z1 = Feet(Num(topLevel, "elevation"));
                IList centerline = Arr(wall["centerline"]);
                if (centerline.Count < 2)
                {
                    continue;
                }
                XYZ p0 = Point2(Obj(centerline[0]), Math.Min(z0, z1));
                XYZ p1 = Point2(Obj(centerline[centerline.Count - 1]), Math.Min(z0, z1));
                double thickness = Feet(Num(wall, "thickness", 250));
                IList<XYZ> footprint = ThickLineFootprint(p0, p1, thickness);
                string label = id + " t" + Num(wall, "thickness", 250).ToString("0") + "mm";
                DirectShape ds = CreateExtrudedShape(doc, BuiltInCategory.OST_Walls, label, footprint, Math.Abs(z1 - z0));
                Stamp(ds, id, "wall", label);
            }
        }

        private static void ImportBeams(Document doc, IList beams, Dictionary<string, object> levelLookup, Dictionary<string, object> sectionLookup)
        {
            foreach (object item in beams)
            {
                Dictionary<string, object> beam = Obj(item);
                string id = Str(beam, "id");
                DeleteExistingByJsonId(doc, id);
                Dictionary<string, object> level = Obj(levelLookup[Str(beam, "level_id")]);
                double z = Feet(Num(level, "elevation"));
                Dictionary<string, object> section = GetSection(sectionLookup, Str(beam, "section_seed_id"));
                Dictionary<string, object> geom = section.ContainsKey("geometry") ? Obj(section["geometry"]) : new Dictionary<string, object>();
                double width = Feet(Num(geom, "b_mm", 300));
                double depth = Feet(Num(geom, "h_mm", 600));
                XYZ p0 = Point2(Obj(beam["start"]), z);
                XYZ p1 = Point2(Obj(beam["end"]), z);
                IList<XYZ> footprint = ThickLineFootprint(p0, p1, width);
                string label = id + " " + SectionLabel(section);
                DirectShape ds = CreateExtrudedShape(doc, BuiltInCategory.OST_StructuralFraming, label, footprint, depth);
                Stamp(ds, id, "beam", SectionLabel(section));
            }
        }

        private static void ImportSlabs(Document doc, IList slabs, Dictionary<string, object> levelLookup)
        {
            foreach (object item in slabs)
            {
                Dictionary<string, object> slab = Obj(item);
                string id = Str(slab, "id");
                DeleteExistingByJsonId(doc, id);
                Dictionary<string, object> level = Obj(levelLookup[Str(slab, "level_id")]);
                double z = Feet(Num(level, "elevation"));
                double thickness = Feet(Num(slab, "thickness_seed", 200));
                IList<XYZ> footprint = PolygonFootprint(Arr(slab["boundary"]), z);
                string label = id + " t" + Num(slab, "thickness_seed", 200).ToString("0") + "mm";
                DirectShape ds = CreateExtrudedShape(doc, BuiltInCategory.OST_Floors, label, footprint, thickness);
                Stamp(ds, id, "slab", label);
            }
        }

        private static void ImportOpenings(Document doc, IList openings, Dictionary<string, object> levelLookup)
        {
            foreach (object item in openings)
            {
                Dictionary<string, object> opening = Obj(item);
                string id = Str(opening, "id");
                DeleteExistingByJsonId(doc, id);
                Dictionary<string, object> level = Obj(levelLookup[Str(opening, "level_id")]);
                double z = Feet(Num(level, "elevation")) + Feet(100);
                IList<XYZ> footprint = PolygonFootprint(Arr(opening["boundary"]), z);
                DirectShape ds = CreateExtrudedShape(doc, BuiltInCategory.OST_GenericModel, id + " opening placeholder", footprint, Feet(150));
                Stamp(ds, id, "opening-placeholder");
            }
        }

        private static void ImportReviewNotes(Document doc, Dictionary<string, object> intent, Dictionary<string, object> sectionLookup, Dictionary<string, object> levelLookup)
        {
            ElementId textTypeId = FindDefaultTextNoteTypeId(doc);
            if (textTypeId == ElementId.InvalidElementId)
            {
                return;
            }

            IList levels = Arr(intent["levels"]);
            foreach (object item in levels)
            {
                Dictionary<string, object> level = Obj(item);
                string levelId = Str(level, "id");
                Autodesk.Revit.DB.View view = FindViewByName(doc, "GBP " + Str(level, "name", levelId));
                if (view == null)
                {
                    continue;
                }

                DeleteExistingReviewNotes(doc, view);
                string note = BuildLevelReviewNote(level, intent, sectionLookup, levelLookup);
                TextNote.Create(doc, view.Id, new XYZ(Feet(2000), Feet(108000), 0), note, textTypeId);
            }
        }

        private static string BuildLevelReviewNote(Dictionary<string, object> level, Dictionary<string, object> intent, Dictionary<string, object> sectionLookup, Dictionary<string, object> levelLookup)
        {
            string levelId = Str(level, "id");
            SortedSet<string> columnSections = new SortedSet<string>();
            SortedSet<string> beamSections = new SortedSet<string>();
            SortedSet<string> wallSections = new SortedSet<string>();
            SortedSet<string> slabSections = new SortedSet<string>();

            foreach (object item in Arr(intent["columns"]))
            {
                Dictionary<string, object> column = Obj(item);
                if (level_in_range_for_note(level, column, levelLookup))
                {
                    columnSections.Add(SectionLabel(GetSection(sectionLookup, Str(column, "section_seed_id"))));
                }
            }
            foreach (object item in Arr(intent["beams"]))
            {
                Dictionary<string, object> beam = Obj(item);
                if (Str(beam, "level_id") == levelId)
                {
                    beamSections.Add(SectionLabel(GetSection(sectionLookup, Str(beam, "section_seed_id"))));
                }
            }
            foreach (object item in Arr(intent["walls"]))
            {
                Dictionary<string, object> wall = Obj(item);
                if (level_in_range_for_note(level, wall, levelLookup))
                {
                    wallSections.Add("t" + Num(wall, "thickness", 0).ToString("0") + "mm");
                }
            }
            foreach (object item in Arr(intent["slabs"]))
            {
                Dictionary<string, object> slab = Obj(item);
                if (Str(slab, "level_id") == levelId)
                {
                    slabSections.Add("t" + Num(slab, "thickness_seed", 0).ToString("0") + "mm");
                }
            }

            return "GBP STRUCTURAL PIPELINE REVIEW - " + Str(level, "name", levelId) + "\n"
                + "Status: review-grade; dimensions are seed sizes pending formal analysis.\n"
                + "Columns: " + JoinOrNone(columnSections) + "\n"
                + "Beams: " + JoinOrNone(beamSections) + "\n"
                + "Walls: " + JoinOrNone(wallSections) + "\n"
                + "Slabs: " + JoinOrNone(slabSections) + "\n"
                + "Source of truth: neutral JSON / GBP_JSON_ID.";
        }

        private static bool level_in_range_for_note(Dictionary<string, object> level, Dictionary<string, object> item, Dictionary<string, object> levelLookup)
        {
            string baseLevelId = Str(item, "base_level_id");
            string topLevelId = Str(item, "top_level_id");
            if (string.IsNullOrEmpty(baseLevelId) || string.IsNullOrEmpty(topLevelId))
            {
                return true;
            }
            Dictionary<string, object> baseLevel = Obj(levelLookup[baseLevelId]);
            Dictionary<string, object> topLevel = Obj(levelLookup[topLevelId]);
            double z = Num(level, "elevation");
            double z0 = Math.Min(Num(baseLevel, "elevation"), Num(topLevel, "elevation"));
            double z1 = Math.Max(Num(baseLevel, "elevation"), Num(topLevel, "elevation"));
            return z >= z0 && z <= z1;
        }

        private static string JoinOrNone(SortedSet<string> values)
        {
            if (values.Count == 0)
            {
                return "none";
            }
            return string.Join("; ", values);
        }

        private static ElementId FindDefaultTextNoteTypeId(Document doc)
        {
            FilteredElementCollector collector = new FilteredElementCollector(doc).OfClass(typeof(TextNoteType));
            foreach (Element element in collector)
            {
                return element.Id;
            }
            return ElementId.InvalidElementId;
        }

        private static void DeleteExistingReviewNotes(Document doc, Autodesk.Revit.DB.View view)
        {
            List<ElementId> toDelete = new List<ElementId>();
            FilteredElementCollector collector = new FilteredElementCollector(doc, view.Id).OfClass(typeof(TextNote));
            foreach (Element element in collector)
            {
                TextNote note = element as TextNote;
                if (note != null && note.Text != null && note.Text.StartsWith("GBP STRUCTURAL PIPELINE REVIEW"))
                {
                    toDelete.Add(note.Id);
                }
            }
            if (toDelete.Count > 0)
            {
                doc.Delete(toDelete);
            }
        }

        private static DirectShape CreateExtrudedShape(Document doc, BuiltInCategory category, string name, IList<XYZ> footprint, double height)
        {
            DirectShape ds = DirectShape.CreateElement(doc, new ElementId(category));
            ds.ApplicationId = AppId;
            ds.ApplicationDataId = name;
            ds.Name = name;
            CurveLoop loop = new CurveLoop();
            for (int i = 0; i < footprint.Count; i++)
            {
                XYZ a = footprint[i];
                XYZ b = footprint[(i + 1) % footprint.Count];
                if (a.DistanceTo(b) > 0.0001)
                {
                    loop.Append(Line.CreateBound(a, b));
                }
            }
            IList<CurveLoop> loops = new List<CurveLoop>();
            loops.Add(loop);
            Solid solid = GeometryCreationUtilities.CreateExtrusionGeometry(loops, XYZ.BasisZ, Math.Max(height, Feet(50)));
            IList<GeometryObject> geometry = new List<GeometryObject>();
            geometry.Add(solid);
            ds.SetShape(geometry);
            return ds;
        }

        private static void ImportStructuralPlanViews(Document doc, IList levels)
        {
            ViewFamilyType viewFamilyType = FindPlanViewFamilyType(doc, ViewFamily.StructuralPlan) ?? FindPlanViewFamilyType(doc, ViewFamily.FloorPlan);
            if (viewFamilyType == null)
            {
                return;
            }

            foreach (object item in levels)
            {
                Dictionary<string, object> levelData = Obj(item);
                string id = Str(levelData, "id");
                string name = "GBP " + Str(levelData, "name", id);
                if (FindViewByName(doc, name) != null)
                {
                    continue;
                }
                Level level = FindLevelByName(doc, Str(levelData, "name", id));
                if (level == null)
                {
                    continue;
                }
                ViewPlan view = ViewPlan.Create(doc, viewFamilyType.Id, level.Id);
                SafeSetName(view, name);
                view.DetailLevel = ViewDetailLevel.Fine;
            }
        }

        private static ViewFamilyType FindPlanViewFamilyType(Document doc, ViewFamily viewFamily)
        {
            FilteredElementCollector collector = new FilteredElementCollector(doc).OfClass(typeof(ViewFamilyType));
            foreach (Element element in collector)
            {
                ViewFamilyType type = element as ViewFamilyType;
                if (type != null && type.ViewFamily == viewFamily)
                {
                    return type;
                }
            }
            return null;
        }

        private static Autodesk.Revit.DB.View FindViewByName(Document doc, string name)
        {
            FilteredElementCollector collector = new FilteredElementCollector(doc).OfClass(typeof(Autodesk.Revit.DB.View));
            foreach (Element element in collector)
            {
                Autodesk.Revit.DB.View view = element as Autodesk.Revit.DB.View;
                if (view != null && !view.IsTemplate && view.Name == name)
                {
                    return view;
                }
            }
            return null;
        }

        private static IList<XYZ> Rectangle(double x, double y, double b, double h, double z)
        {
            double bx = b / 2.0;
            double hy = h / 2.0;
            return new List<XYZ>
            {
                new XYZ(x - bx, y - hy, z),
                new XYZ(x + bx, y - hy, z),
                new XYZ(x + bx, y + hy, z),
                new XYZ(x - bx, y + hy, z)
            };
        }

        private static IList<XYZ> ThickLineFootprint(XYZ p0, XYZ p1, double width)
        {
            XYZ v = p1 - p0;
            double length = Math.Sqrt(v.X * v.X + v.Y * v.Y);
            if (length < 0.0001)
            {
                return Rectangle(p0.X, p0.Y, width, width, p0.Z);
            }
            double nx = -v.Y / length;
            double ny = v.X / length;
            double t = width / 2.0;
            return new List<XYZ>
            {
                new XYZ(p0.X + nx * t, p0.Y + ny * t, p0.Z),
                new XYZ(p0.X - nx * t, p0.Y - ny * t, p0.Z),
                new XYZ(p1.X - nx * t, p1.Y - ny * t, p1.Z),
                new XYZ(p1.X + nx * t, p1.Y + ny * t, p1.Z)
            };
        }

        private static IList<XYZ> PolygonFootprint(IList points, double z)
        {
            List<XYZ> result = new List<XYZ>();
            for (int i = 0; i < points.Count; i++)
            {
                Dictionary<string, object> point = Obj(points[i]);
                XYZ xyz = Point2(point, z);
                if (result.Count == 0 || result[result.Count - 1].DistanceTo(xyz) > 0.0001)
                {
                    result.Add(xyz);
                }
            }
            if (result.Count > 1 && result[0].DistanceTo(result[result.Count - 1]) < 0.0001)
            {
                result.RemoveAt(result.Count - 1);
            }
            return result;
        }

        private static XYZ Point2(Dictionary<string, object> point, double z)
        {
            return new XYZ(Feet(Num(point, "x")), Feet(Num(point, "y")), z);
        }

        private static Dictionary<string, object> BuildLookup(IList items)
        {
            Dictionary<string, object> lookup = new Dictionary<string, object>();
            foreach (object item in items)
            {
                Dictionary<string, object> obj = Obj(item);
                lookup[Str(obj, "id")] = obj;
            }
            return lookup;
        }

        private static Dictionary<string, object> GetSection(Dictionary<string, object> sectionLookup, string id)
        {
            if (!string.IsNullOrEmpty(id) && sectionLookup.ContainsKey(id))
            {
                return Obj(sectionLookup[id]);
            }
            return new Dictionary<string, object>();
        }

        private static string SectionLabel(Dictionary<string, object> section)
        {
            if (section == null || section.Count == 0)
            {
                return "section-unassigned";
            }
            string name = Str(section, "name", Str(section, "id", "section"));
            if (!section.ContainsKey("geometry"))
            {
                return name;
            }
            Dictionary<string, object> geom = Obj(section["geometry"]);
            if (geom.ContainsKey("b_mm") && geom.ContainsKey("h_mm"))
            {
                return name + " " + Num(geom, "b_mm").ToString("0") + "x" + Num(geom, "h_mm").ToString("0");
            }
            if (geom.ContainsKey("thickness_mm"))
            {
                return name + " t" + Num(geom, "thickness_mm").ToString("0");
            }
            return name;
        }

        private static void EnsureJsonIdParameter(Autodesk.Revit.ApplicationServices.Application app, Document doc)
        {
            string original = app.SharedParametersFilename;
            string tempPath = Path.Combine(Path.GetTempPath(), "gbp_structural_pipeline_shared_parameters.txt");
            if (!File.Exists(tempPath))
            {
                File.WriteAllText(tempPath, "# GBP Structural Pipeline shared parameters\n");
            }
            app.SharedParametersFilename = tempPath;
            DefinitionFile file = app.OpenSharedParameterFile();
            DefinitionGroup group = file.Groups.get_Item("GBP Structural Pipeline") ?? file.Groups.Create("GBP Structural Pipeline");

            CategorySet categories = app.Create.NewCategorySet();
            AddCategory(doc, categories, BuiltInCategory.OST_Levels);
            AddCategory(doc, categories, BuiltInCategory.OST_Grids);
            AddCategory(doc, categories, BuiltInCategory.OST_StructuralColumns);
            AddCategory(doc, categories, BuiltInCategory.OST_StructuralFraming);
            AddCategory(doc, categories, BuiltInCategory.OST_Walls);
            AddCategory(doc, categories, BuiltInCategory.OST_Floors);
            AddCategory(doc, categories, BuiltInCategory.OST_GenericModel);

            EnsureTextParameter(app, doc, group, categories, ParamName);
            EnsureTextParameter(app, doc, group, categories, ParamRole);
            EnsureTextParameter(app, doc, group, categories, ParamSection);
            EnsureTextParameter(app, doc, group, categories, ParamStatus);
            EnsureTextParameter(app, doc, group, categories, ParamSource);
            app.SharedParametersFilename = original;
        }

        private static void EnsureTextParameter(Autodesk.Revit.ApplicationServices.Application app, Document doc, DefinitionGroup group, CategorySet categories, string name)
        {
            Definition definitionToBind = group.Definitions.get_Item(name);
            if (definitionToBind == null)
            {
                ExternalDefinitionCreationOptions options = new ExternalDefinitionCreationOptions(name, SpecTypeId.String.Text);
                definitionToBind = group.Definitions.Create(options);
            }

            InstanceBinding binding = app.Create.NewInstanceBinding(categories);
            if (!doc.ParameterBindings.Insert(definitionToBind, binding, BuiltInParameterGroup.PG_DATA))
            {
                doc.ParameterBindings.ReInsert(definitionToBind, binding, BuiltInParameterGroup.PG_DATA);
            }
        }

        private static void AddCategory(Document doc, CategorySet categories, BuiltInCategory builtInCategory)
        {
            Category category = doc.Settings.Categories.get_Item(builtInCategory);
            if (category != null && !categories.Contains(category))
            {
                categories.Insert(category);
            }
        }

        private static Element FindByJsonId(Document doc, string jsonId)
        {
            if (string.IsNullOrEmpty(jsonId))
            {
                return null;
            }
            FilteredElementCollector collector = new FilteredElementCollector(doc).WhereElementIsNotElementType();
            foreach (Element element in collector)
            {
                Parameter parameter = element.LookupParameter(ParamName);
                if (parameter != null && parameter.AsString() == jsonId)
                {
                    return element;
                }
                DirectShape ds = element as DirectShape;
                if (ds != null && ds.ApplicationId == AppId && ds.ApplicationDataId != null && ds.ApplicationDataId.StartsWith(jsonId))
                {
                    return element;
                }
            }
            return null;
        }

        private static void DeleteExistingByJsonId(Document doc, string jsonId)
        {
            Element existing = FindByJsonId(doc, jsonId);
            if (existing != null)
            {
                doc.Delete(existing.Id);
            }
        }

        private static Level FindLevelByName(Document doc, string name)
        {
            FilteredElementCollector collector = new FilteredElementCollector(doc).OfClass(typeof(Level));
            foreach (Element element in collector)
            {
                if (element.Name == name)
                {
                    return element as Level;
                }
            }
            return null;
        }

        private static void Stamp(Element element, string jsonId, string role, string section = "")
        {
            SetTextParameter(element, ParamName, jsonId);
            SetTextParameter(element, ParamRole, role);
            SetTextParameter(element, ParamSection, section);
            SetTextParameter(element, ParamStatus, "review-grade; not analysis-verified");
            SetTextParameter(element, ParamSource, "neutral JSON / GBP Structural Pipeline");
            Parameter mark = element.get_Parameter(BuiltInParameter.ALL_MODEL_MARK);
            if (mark != null && !mark.IsReadOnly)
            {
                mark.Set(jsonId);
            }
            Parameter comments = element.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS);
            if (comments != null && !comments.IsReadOnly)
            {
                comments.Set("GBP Structural Pipeline " + role + " " + section + " from neutral JSON: " + jsonId);
            }
        }

        private static void SetTextParameter(Element element, string name, string value)
        {
            Parameter parameter = element.LookupParameter(name);
            if (parameter != null && !parameter.IsReadOnly)
            {
                parameter.Set(value ?? "");
            }
        }

        private static void SafeSetName(Element element, string name)
        {
            try
            {
                if (!string.IsNullOrEmpty(name))
                {
                    element.Name = name;
                }
            }
            catch
            {
                // Name collisions are non-fatal; the GBP_JSON_ID parameter remains the stable identity.
            }
        }

        private static Dictionary<string, object> Obj(object value)
        {
            Dictionary<string, object> obj = value as Dictionary<string, object>;
            if (obj == null)
            {
                throw new InvalidOperationException("Expected JSON object.");
            }
            return obj;
        }

        private static IList Arr(object value)
        {
            IList list = value as IList;
            if (list == null)
            {
                throw new InvalidOperationException("Expected JSON array.");
            }
            return list;
        }

        private static string Str(Dictionary<string, object> obj, string key)
        {
            return Str(obj, key, "");
        }

        private static string Str(Dictionary<string, object> obj, string key, string defaultValue)
        {
            if (!obj.ContainsKey(key) || obj[key] == null)
            {
                return defaultValue;
            }
            return Convert.ToString(obj[key]);
        }

        private static double Num(Dictionary<string, object> obj, string key)
        {
            return Num(obj, key, 0.0);
        }

        private static double Num(Dictionary<string, object> obj, string key, double defaultValue)
        {
            if (!obj.ContainsKey(key) || obj[key] == null)
            {
                return defaultValue;
            }
            return Convert.ToDouble(obj[key]);
        }

        private static double Feet(double mm)
        {
            return mm * MmToFeet;
        }
    }
}
