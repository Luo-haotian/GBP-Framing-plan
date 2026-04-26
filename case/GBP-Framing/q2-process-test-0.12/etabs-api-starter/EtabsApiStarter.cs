using System;
using ETABSv1;

namespace GbpEtabsStarter
{
    internal static class Program
    {
        private static void Check(int ret, string step)
        {
            if (ret != 0)
            {
                throw new InvalidOperationException(step + " failed. ETABS API return code = " + ret);
            }
            Console.WriteLine("OK: " + step);
        }

        private static void Main()
        {
            string etabsExe = @"C:\Program Files\Computers and Structures\ETABS 21\ETABS.exe";
            string outputModel = @"C:\Users\11131\Desktop\Codex\GBP-Framing Plan v2\run-001\outputs\etabs_api_starter_blank.edb";

            cHelper helper = new Helper();

            // Either form works on this installation. CreateObject uses the exact EXE path;
            // CreateObjectProgID uses the registered COM ProgID.
            cOAPI etabs = helper.CreateObject(etabsExe);
            // cOAPI etabs = helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject");

            Check(etabs.ApplicationStart(), "start ETABS");

            cSapModel sap = etabs.SapModel;
            Check(sap.InitializeNewModel(eUnits.kN_m_C), "initialize new model in kN-m-C");
            Check(sap.File.NewBlank(), "create blank model");

            // Minimal materials and frame sections. Dimensions are in meters because units are kN-m-C.
            Check(sap.PropMaterial.SetMaterial("C45", eMatType.Concrete, -1, "", ""), "define C45 material");
            Check(sap.PropMaterial.SetMPIsotropic("C45", 34500000, 0.2, 9.9e-6, 0), "set C45 elastic properties");
            Check(sap.PropFrame.SetRectangle("COL_900x900", "C45", 0.9, 0.9, -1, "starter column", ""), "define column section");
            Check(sap.PropFrame.SetRectangle("BM_700x1100", "C45", 1.1, 0.7, -1, "starter beam", ""), "define beam section");

            string columnName = "";
            Check(sap.FrameObj.AddByCoord(0, 0, 0, 0, 0, 5, ref columnName, "COL_900x900", "COL-STARTER", "Global"), "add starter column");

            string beamName = "";
            Check(sap.FrameObj.AddByCoord(0, 0, 5, 8, 0, 5, ref beamName, "BM_700x1100", "BM-STARTER", "Global"), "add starter beam");

            Check(sap.File.Save(outputModel), "save starter EDB");

            Console.WriteLine("Saved: " + outputModel);
            Console.WriteLine("You can now inspect the model in ETABS. Close ETABS manually when finished.");
        }
    }
}
