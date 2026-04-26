# Capacity And Sizing Check - v0.15

Date: 2026-04-26  
Source JSON: `neutral_structural_model_v0_15_sized_review.json`  
Review DXF: `structural_review_v0_15_sized_review.dxf`

## 1. Why v0.14 Was Not Reasonable

v0.14 used `1200x1200` columns for all low-rise mall/podium columns. That was too blunt.

For only a few podium/mall levels, a 1200 square RC column has far more axial capacity than many edge/perimeter locations need, and it damages the mall space. It may still be needed at special transfer or tower-load collection locations, but it should not be the default mall column size.

v0.15 changes the default sizing strategy:

| Member | v0.14 | v0.15 |
| --- | ---: | ---: |
| Mall edge/perimeter columns | 1200x1200 | 700x700 |
| Mall typical columns | 1200x1200 | 900x900 |
| Mall transfer-critical line columns | 1200x1200 | 1000x1000 |
| Tower columns | 900x900 | 900x900, unchanged pending tower load take-down |
| Mall primary beams | 800x1500 | 700x1100 PT/RC band concept |
| Mall secondary beams | 600x1200 | 500x900 PT band concept |
| Office typical beams | 650x1300 | 450x650 slim composite/PT envelope |
| Opening edge beams | 500x1000 | 400x800 |

Current model count remains:

- columns: 70
- beams: 721
- close column pairs under 2m: 0

## 2. Column Capacity Screen

Screening formula only, not final code design:

```text
N_screen = 0.40 fcu Ag + 0.75 fy As
fcu = 45 N/mm2
fy = 500 N/mm2
rho = As / Ag
```

| Column | rho | Concrete term | Steel term | N_screen | Comment |
| --- | ---: | ---: | ---: | ---: | --- |
| 700x700 | 1.5% | 8.82 MN | 2.76 MN | 11.58 MN | suitable for edge/perimeter low-rise screening |
| 700x700 | 2.0% | 8.82 MN | 3.68 MN | 12.50 MN | reserve if edge reactions are high |
| 900x900 | 1.5% | 14.58 MN | 4.56 MN | 19.14 MN | suitable for typical mall screening, but tight if 4 full loaded floors govern |
| 900x900 | 1.8% | 14.58 MN | 5.47 MN | 20.05 MN | more realistic target for internal mall columns |
| 1000x1000 | 1.5% | 18.00 MN | 5.63 MN | 23.63 MN | transfer-critical line seed |
| 1000x1000 | 2.0% | 18.00 MN | 7.50 MN | 25.50 MN | reserve for transfer/tower reaction uncertainty |
| 1200x1200 | 1.5% | 25.92 MN | 8.10 MN | 34.02 MN | over-large for ordinary few-level mall columns |

## 3. Column Load-Take-Down Screen

Assumptions:

```text
Podium slab self-weight = 0.30 x 25 = 7.5 kPa
Finishes/services = 2.0 kPa
Mall live load screen = 5.0 kPa
ULS area load = 1.4 x 9.5 + 1.6 x 5.0 = 21.3 kPa
```

Approximate demand:

| Location | Tributary area | Floors counted | Floor load | Approx demand before beam/transfer allowance | v0.15 size comment |
| --- | ---: | ---: | ---: | ---: | --- |
| Edge/perimeter | 8m x 16m = 128m2 | 3 | 21.3 kPa | 8.18 MN | 700x700 OK as screening with limited allowance |
| Typical internal mall | 16m x 16m = 256m2 | 3 | 21.3 kPa | 16.36 MN | 900x900 OK but should target about 1.5%-1.8% rho |
| Typical internal mall, 4 loaded floors | 256m2 | 4 | 21.3 kPa | 21.81 MN | 900x900 is not enough with allowances; use 1000x1000/local transfer if this governs |
| Transfer-critical line | varies | transfer/tower affected | not just slab load | project-specific | 1000x1000 kept as seed, not final |

Conclusion: `1200x1200` was not a reasonable default for every low-rise mall column. v0.15 is more reasonable, but transfer lines still need real tower reaction load-take-down before approval.

## 4. Beam Sizing Screen

### Mall Secondary Beam 500x900

For a 16m span and 7.5m tributary width:

```text
wu ~= 21.3 x 7.5 + beam self-weight
beam self-weight ~= 0.5 x 0.9 x 25 = 11.25 kN/m
wu ~= 171 kN/m
Mu ~= wu L^2 / 10 = 171 x 16^2 / 10 = 4.38 MNm
```

Ordinary RC check, if `rho = 2.5%`:

```text
b = 500mm, h = 900mm, d ~= 810mm
As = 0.025 x 500 x 810 = 10,125 mm2
M_screen ~= 0.87 fy As 0.9d = 3.22 MNm
```

Conclusion: `500x900` is **not acceptable as ordinary RC** for the full 16m case. It is only a review seed if the system is PT, composite, or the final layout reduces tributary width/span. This is exactly why it must not be marked final design.

### Mall Primary Beam 700x1100

If `rho = 2.0%`:

```text
b = 700mm, h = 1100mm, d ~= 990mm
As = 0.02 x 700 x 990 = 13,860 mm2
M_screen ~= 5.37 MNm
```

Expected long-span primary beam demand can be in the `6-8 MNm` range once secondary beam reactions and transfer effects are included.

Conclusion: `700x1100` improves headroom compared with `800x1500`, but final design likely needs PT force, local thickening, composite steel, or selected deeper transfer beams.

### Office Typical Beam 450x650

The old `650x1300` RC downstand beam was too deep for office space. v0.15 uses a `450x650` slim composite/PT envelope.

This should not be checked as an ordinary RC beam. For a 15m-16m office span, a normal RC beam with 650mm depth would generally be too flexible. The intended interpretation is:

- composite steel beam inside a 650mm structural zone, or
- PT band/slab system, or
- another long-span floor system selected during formal design.

Conclusion: v0.15 preserves office headroom, but it changes the structural system assumption. Formal deflection/vibration/fire design is mandatory.

## 5. Review Decision

v0.15 is more reasonable for architectural review than v0.14 because it reduces oversized columns and office beam depth.

It is **not** a final structural pass. The next real engineering step is a gravity + lateral analysis model with:

- tributary load take-down by column line,
- tower reaction transfer into podium columns/walls,
- PT/composite beam design for long spans,
- deflection and vibration checks,
- punching/joint/shear checks,
- foundation reaction checks.
