# prenatalppkt data dictionary

Cross-source field inventory for the prenatalppkt ETL: every leaf path in the CUIMC Observer JSON corpus and every OBX-3 identifier in the EVMS GE HL7 v2.4 corpus, grouped into a small set of clinical clusters so reviewers can compare the two surfaces side by side.

`docs/data_dictionary/comparison.csv` is the canonical artifact (1135 rows: 761 Observer paths, 374 HL7 identifiers). This README is generated from it; edit `render_readme.py` or `clusters.yaml`, not this file.

## Regenerate

```bash
uv run python src/prenatalppkt/scripts/data_dict/extract_all.py
uv run python src/prenatalppkt/scripts/data_dict/render_readme.py
```

## Schema

Each row in `comparison.csv` is either an Observer leaf path or an HL7 OBX-3 identifier (never both). The 10 columns:

`cluster`, `observer_path`, `observer_type`, `observer_sample`, `observer_n_files`, `viewpoint_path`, `viewpoint_type`, `viewpoint_sample`, `viewpoint_n_files`, `notes`.

## Type tokens

`null`, `bool`, `int`, `float`, `str`, `list`, `dict`, `percentile_str` (e.g. `45%`, `<5%`), `weeks_days_str` (e.g. `20w 3d`). HL7 viewpoint cells append the declared OBX-2 type in parens (`ST`, `NM`, `DT`, `TM`, `TS`).

## Clusters

### amniotic_fluid

Amniotic fluid index, single deepest pocket, and the GE amniotic-fluid measurement family.

_11 Observer paths, 7 HL7 identifiers._

#### Observer (CUIMC JSON)

| observer_path | type | sample | files |
| --- | --- | --- | --- |
| `fetuses[].amioticfluid` | `dict` | - | 5/5 |
| `fetuses[].amioticfluid.amniotic_fluid` | `dict` | - | 5/5 |
| `fetuses[].amioticfluid.amniotic_fluid.afi_done` | `int` | `0\|1` | 5/5 |
| `fetuses[].amioticfluid.amniotic_fluid.afi_total` | `float` | `11.5` | 1/5 |
| `fetuses[].amioticfluid.amniotic_fluid.amniotic_fluid_volume` | `str` | `Normal` | 5/5 |
| `fetuses[].amioticfluid.amniotic_fluid.done` | `int` | `1` | 5/5 |
| `fetuses[].amioticfluid.amniotic_fluid.largest_vertical_pocket` | `float\|int` | `5\|3.7` | 2/5 |
| `fetuses[].amioticfluid.amniotic_fluid.percentile_for_display` | `percentile_str` | `16%` | 1/5 |
| `fetuses[].amioticfluid.amniotic_fluid.quadrant_2` | `float` | `3.5` | 1/5 |
| `fetuses[].amioticfluid.amniotic_fluid.quadrant_3` | `float` | `4.5` | 1/5 |
| `fetuses[].amioticfluid.amniotic_fluid.quadrant_4` | `float` | `3.5` | 1/5 |

#### EVMS GE HL7

| viewpoint_path | type | sample | files |
| --- | --- | --- | --- |
| `OBX Fetus.AmnioticFluidAmount` | `str (ST)` | `oligohydramnios\|normal` | 2/7 |
| `OBX Fetus.AmnioticFluidMaximumVerticalPocket` | `str (NM)` | `1.62\|2.03\|5.36\|4.6\|3.35\|4.27` | 6/7 |
| `OBX Fetus.VP_AmnioticFluidDetails_Mask` | `str (ST)` | `Normal amount with MVP of 5.4 cm\.br\\.br\` | 1/7 |
| `OBX Fetus.VP_AmnioticFluidMaximumVerticalPocket_Author` | `str (ST)` | `Magann` | 6/7 |
| `OBX Fetus.VP_AmnioticFluidMaximumVerticalPocket_DevRatio` | `str (NM)` | `-65.5\|-52.9\|14\|-4.3\|-30.2\|-8.6` | 6/7 |
| `OBX Fetus.VP_AmnioticFluidMaximumVerticalPocket_Deviation` | `str (NM)` | `-3.2\|-2.5\|0.5\|-0.2\|-1.3\|-0.4` | 6/7 |
| `OBX Fetus.VP_AmnioticFluidMaximumVerticalPocket_Percentile` | `str (NM)` | `0\|1\|70\|43\|9\|34` | 6/7 |

### anatomy

Fetal organ-system anatomy: brain, face, GI tract, chest, spine, urinary tract, plus the Observer per-system anatomy array.

_19 Observer paths, 72 HL7 identifiers._

#### Observer (CUIMC JSON)

| observer_path | type | sample | files |
| --- | --- | --- | --- |
| `fetuses[].anatomy[]` | `dict` | - | 5/5 |
| `fetuses[].anatomy[].anomalies` | `list\|null` | - | 5/5 |
| `fetuses[].anatomy[].anomalies[]` | `dict` | - | 5/5 |
| `fetuses[].anatomy[].anomalies[].abnormal_or_normal_variant` | `str` | `Abnormal` | 5/5 |
| `fetuses[].anatomy[].anomalies[].description` | `str` | `Dandy Walker\|Renal agenesis\|Omphalocele\|Acrania\|Hypoplastic left ventricle` | 5/5 |
| `fetuses[].anatomy[].detail` | `list\|null` | - | 5/5 |
| `fetuses[].anatomy[].detail[]` | `dict` | - | 5/5 |
| `fetuses[].anatomy[].detail[].anat_det_state` | `str` | `Unseen\|Abnormal\|Normal` | 5/5 |
| `fetuses[].anatomy[].detail[].label` | `str` | `Calvarium\|BPD Level\|Lateral Ventricles\|Choroid Plexus\|Cerebellum\|Cisterna Magna\|Neck\|Nuchal Fold\|Profile\|Orbits\|...` | 5/5 |
| `fetuses[].anatomy[].detail[].print_in_report` | `int` | `0\|1` | 5/5 |
| `fetuses[].anatomy[].detail[].required` | `str` | `No` | 5/5 |
| `fetuses[].anatomy[].detail[].required_condition_met` | `str` | `No` | 5/5 |
| `fetuses[].anatomy[].main` | `dict` | - | 5/5 |
| `fetuses[].anatomy[].main.anat_state` | `str` | `Abnormal\|Normal\|See details\|Unseen` | 5/5 |
| `fetuses[].anatomy[].main.label` | `str` | `Head\|Face/Neck\|Th. Cav.\|Heart\|Abd. Cav.\|Stomach\|Right Kidney\|Left Kidney\|Bladder\|Abd. Wall\|...` | 5/5 |
| `fetuses[].anatomy[].main.main_txt` | `str` | `Abnormalities in the head were noted during this scan; please see the anatomy comments.\|The fetal face appears normal.\|Anatomy of the fetal thorax appeared within normal limits.\|The cardiac size and structures appeared sonographically normal at the four chamber view, and cardiac rhythm was regular.\|The abdominal cavity appears normal.\|The fetal stomach appears normal.\|The right kidney appears within normal limits with respect to size, collection systems, and parenchyma.\|The left kidney appears within normal limits with respect to size, collection systems, and parenchyma.\|The fetal bladder appears normal.\|The abdominal wall appears intact.\|...` | 5/5 |
| `fetuses[].anatomy[].main.print_in_report` | `int` | `1\|0` | 5/5 |
| `fetuses[].anatomy[].main.required` | `str` | `Yes\|No` | 5/5 |
| `fetuses[].anatomy[].main.required_condition_met` | `str` | `Yes` | 5/5 |

#### EVMS GE HL7

| viewpoint_path | type | sample | files |
| --- | --- | --- | --- |
| `OBX BrainFetus.BrainAppearance` | `str (ST)` | `abnormal\|normal` | 6/7 |
| `OBX BrainFetus.CerebellumAppearance` | `str (ST)` | `abnormal` | 1/7 |
| `OBX BrainFetus.CerebellumDetails` | `str (ST)` | `hypoplasia` | 1/7 |
| `OBX BrainFetus.LateralVentricleLAppearance` | `str (ST)` | `abnormal` | 2/7 |
| `OBX BrainFetus.LateralVentricleLDetails` | `str (ST)` | `ventriculomegaly` | 2/7 |
| `OBX BrainFetus.LateralVentricleRAppearance` | `str (ST)` | `abnormal` | 3/7 |
| `OBX BrainFetus.LateralVentricleRDetails` | `str (ST)` | `ventriculomegaly` | 3/7 |
| `OBX BrainFetus.LateralVentricleUndefinedOccipitalHorn` | `str (NM)` | `13.78\|12.07\|0.73` | 3/7 |
| `OBX BrainFetus.TranscerebellarDiameter` | `str (NM)` | `19.3` | 1/7 |
| `OBX BrainFetus.VP_TranscerebellarDiameter_Author` | `str (ST)` | `Hill` | 1/7 |
| `OBX BrainFetus.VP_TranscerebellarDiameter_DevRatio` | `str (NM)` | `-3.5` | 1/7 |
| `OBX BrainFetus.VP_TranscerebellarDiameter_Deviation` | `str (NM)` | `-0.7` | 1/7 |
| `OBX BrainFetus.VP_TranscerebellarDiameter_GA` | `str (NM)` | `131` | 1/7 |
| `OBX BrainFetus.VP_TranscerebellarDiameter_Percentile` | `str (NM)` | `26` | 1/7 |
| `OBX ChestFetus.BonyThoracicArea` | `str (NM)` | `1600.67\|2273.55` | 2/7 |
| `OBX ChestFetus.BonyThoracicCircumference` | `str (NM)` | `141.83\|169.03` | 2/7 |
| `OBX ChestFetus.ChestAppearance` | `str (ST)` | `normal` | 6/7 |
| `OBX ChestFetus.VP_BonyThoracicCircumference_Author` | `str (ST)` | `Lessoway` | 2/7 |
| `OBX ChestFetus.VP_BonyThoracicCircumference_DevRatio` | `str (NM)` | `-16.8\|-0.9` | 2/7 |
| `OBX ChestFetus.VP_BonyThoracicCircumference_Deviation` | `str (NM)` | `-2\|-0.1` | 2/7 |
| `OBX ChestFetus.VP_BonyThoracicCircumference_Percentile` | `str (NM)` | `2\|46` | 2/7 |
| `OBX FaceFetus.FaceAppearance` | `str (ST)` | `suboptimal\|normal` | 7/7 |
| `OBX FaceFetus.InnerInterorbitalDistance` | `str (NM)` | `15` | 1/7 |
| `OBX FaceFetus.VP_InnerInterorbitalDistance_Author` | `str (ST)` | `Merz` | 1/7 |
| `OBX GastrointestinalTractFetus.GastrointestinalTractAppearance` | `str (ST)` | `normal` | 6/7 |
| `OBX SpineFetus.SpineAppearance` | `str (ST)` | `suboptimal\|normal` | 7/7 |
| `OBX UrinaryTractFetus.BladderAppearance` | `str (ST)` | `normal` | 2/7 |
| `OBX UrinaryTractFetus.KidneyLAnteriorPosteriorDiameter` | `str (NM)` | `30.9` | 1/7 |
| `OBX UrinaryTractFetus.KidneyLAppearance` | `str (ST)` | `abnormal` | 1/7 |
| `OBX UrinaryTractFetus.KidneyLLongitudinalDiameter` | `str (NM)` | `43.6` | 1/7 |
| `OBX UrinaryTractFetus.KidneyLTransverseDiameter` | `str (NM)` | `45.9` | 1/7 |
| `OBX UrinaryTractFetus.KidneyLVolume` | `str (NM)` | `32378` | 1/7 |
| `OBX UrinaryTractFetus.KidneyRAnteriorPosteriorDiameter` | `str (NM)` | `25.7` | 1/7 |
| `OBX UrinaryTractFetus.KidneyRAppearance` | `str (ST)` | `abnormal` | 1/7 |
| `OBX UrinaryTractFetus.KidneyRLongitudinalDiameter` | `str (NM)` | `45.2` | 1/7 |
| `OBX UrinaryTractFetus.KidneyRTransverseDiameter` | `str (NM)` | `27.5` | 1/7 |
| `OBX UrinaryTractFetus.KidneyRVolume` | `str (NM)` | `16726` | 1/7 |
| `OBX UrinaryTractFetus.RenalPelvisLAnteriorPosteriorDiameter` | `str (NM)` | `13.35` | 1/7 |
| `OBX UrinaryTractFetus.RenalPelvisRAnteriorPosteriorDiameter` | `str (NM)` | `11.18` | 1/7 |
| `OBX UrinaryTractFetus.UrogenitalTractAppearance` | `str (ST)` | `normal\|abnormal` | 6/7 |
| `OBX UrinaryTractFetus.VP_KidneyLAnteriorPosteriorDiameter_Author` | `str (ST)` | `Chitty` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLAnteriorPosteriorDiameter_DevRatio` | `str (NM)` | `32.5` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLAnteriorPosteriorDiameter_Deviation` | `str (NM)` | `1.9` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLAnteriorPosteriorDiameter_Percentile` | `str (NM)` | `97` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLLongitudinalDiameter_Author` | `str (ST)` | `Chitty` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLLongitudinalDiameter_DevRatio` | `str (NM)` | `12.5` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLLongitudinalDiameter_Deviation` | `str (NM)` | `1` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLLongitudinalDiameter_Percentile` | `str (NM)` | `83` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLTransverseDiameter_Author` | `str (ST)` | `Chitty` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLTransverseDiameter_DevRatio` | `str (NM)` | `102.6` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLVolume_Author` | `str (ST)` | `Chitty` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLVolume_DevRatio` | `str (NM)` | `201.8` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLVolume_Deviation` | `str (NM)` | `5.2` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyLVolume_Percentile` | `str (NM)` | `100` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRAnteriorPosteriorDiameter_Author` | `str (ST)` | `Chitty` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRAnteriorPosteriorDiameter_DevRatio` | `str (NM)` | `10.2` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRAnteriorPosteriorDiameter_Deviation` | `str (NM)` | `0.6` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRAnteriorPosteriorDiameter_Percentile` | `str (NM)` | `72` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRLongitudinalDiameter_Author` | `str (ST)` | `Chitty` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRLongitudinalDiameter_DevRatio` | `str (NM)` | `16.6` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRLongitudinalDiameter_Deviation` | `str (NM)` | `1.3` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRLongitudinalDiameter_Percentile` | `str (NM)` | `90` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRTransverseDiameter_Author` | `str (ST)` | `Chitty` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRTransverseDiameter_DevRatio` | `str (NM)` | `21.4` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRTransverseDiameter_Deviation` | `str (NM)` | `1.2` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRTransverseDiameter_Percentile` | `str (NM)` | `89` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRVolume_Author` | `str (ST)` | `Chitty` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRVolume_DevRatio` | `str (NM)` | `55.9` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRVolume_Deviation` | `str (NM)` | `1.4` | 1/7 |
| `OBX UrinaryTractFetus.VP_KidneyRVolume_Percentile` | `str (NM)` | `92` | 1/7 |
| `OBX UrinaryTractFetus.VP_RenalPelvisLAnteriorPosteriorDiameter_Author` | `str (ST)` | `Chitty` | 1/7 |
| `OBX UrinaryTractFetus.VP_RenalPelvisRAnteriorPosteriorDiameter_Author` | `str (ST)` | `Chitty` | 1/7 |

### biometry

Fetal biometric measurements (HC, BPD, AC, FL, etc.), growth ratios, EFW values, first-trimester measurements (CRL, NT), and the GE FGR data block.

_45 Observer paths, 112 HL7 identifiers._

#### Observer (CUIMC JSON)

| observer_path | type | sample | files |
| --- | --- | --- | --- |
| `fetuses[].efws` | `list\|null` | - | 5/5 |
| `fetuses[].efws[]` | `dict` | - | 4/5 |
| `fetuses[].efws[].calculated_percentile` | `float\|int` | `55.6\|63.7\|51.2\|36.3\|52\|53.2\|61.8\|81.1\|65.2\|74.9\|...` | 4/5 |
| `fetuses[].efws[].decimal_paces` | `int` | `0` | 4/5 |
| `fetuses[].efws[].fetus_number` | `int` | `1` | 4/5 |
| `fetuses[].efws[].label` | `str` | `EFW (AC, FL, HC)\|EFW (AC, FL)\|EFW (AC, BPD)` | 4/5 |
| `fetuses[].efws[].percentile_for_display` | `percentile_str` | `56%\|64%\|51%\|36%\|52%\|53%\|62%\|81%\|65%\|75%\|...` | 4/5 |
| `fetuses[].efws[].print_in_report` | `int` | `1\|0` | 4/5 |
| `fetuses[].efws[].range` | `str` | - | 4/5 |
| `fetuses[].efws[].value` | `float` | `1014.828\|1042.214\|1000.887\|598.194\|638.934\|632.184\|2778.253\|2858.504\|3064.597\|1273.729\|...` | 4/5 |
| `fetuses[].firsttrimester` | `dict` | - | 5/5 |
| `fetuses[].firsttrimester.done` | `int` | `0` | 5/5 |
| `fetuses[].firsttrimester.fet_pole_anom_txt` | `str` | - | 5/5 |
| `fetuses[].firsttrimester.fetal_pole` | `str` | `Unspecified\|Abnormal` | 5/5 |
| `fetuses[].firsttrimester.fetal_pole_anomalies` | `null` | - | 5/5 |
| `fetuses[].firsttrimester.fetal_pole_size` | `int` | `0` | 5/5 |
| `fetuses[].firsttrimester.gest_sac_shape` | `str` | `Unspecified\|Normal` | 5/5 |
| `fetuses[].firsttrimester.yolk_sac_pres` | `str` | `Unspecified\|Seen` | 5/5 |
| `fetuses[].firsttrimester.yolk_sac_size_a` | `int` | `0` | 5/5 |
| `fetuses[].firsttrimester.yolk_sac_size_b` | `int` | `0` | 5/5 |
| `fetuses[].firsttrimester.yolk_sac_size_c` | `int` | `0` | 5/5 |
| `fetuses[].firsttrimester.yolk_sac_vol` | `int` | `0` | 5/5 |
| `fetuses[].measurements` | `list` | - | 5/5 |
| `fetuses[].measurements[]` | `dict` | - | 5/5 |
| `fetuses[].measurements[].calculated_ega` | `float\|int` | `26.9\|27.1\|0\|27.4\|23.7\|23.8\|22.3\|23.6\|36.4\|37.9\|...` | 5/5 |
| `fetuses[].measurements[].calculated_percentile` | `float\|int` | `55.6\|51.2\|42.5\|46.8\|0\|50.4\|53.2\|5.1\|33.7\|49.2\|...` | 5/5 |
| `fetuses[].measurements[].calculated_z_score` | `int` | `0` | 5/5 |
| `fetuses[].measurements[].decimal_places` | `int` | `2\|1` | 5/5 |
| `fetuses[].measurements[].fetus_number` | `int` | `1` | 5/5 |
| `fetuses[].measurements[].include_in_avg_ga_calc` | `int` | `1\|0` | 5/5 |
| `fetuses[].measurements[].label` | `str` | `AC\|BPD\|HC\|Femur\|Nuchal Fold\|Cerebellum\|Humerus\|CRL` | 5/5 |
| `fetuses[].measurements[].percentile_for_display` | `percentile_str\|str` | `56%\|51%\|43%\|47%\|\|50%\|53%\|5%\|34%\|49%\|...` | 5/5 |
| `fetuses[].measurements[].print_in_report` | `int` | `1` | 5/5 |
| `fetuses[].measurements[].unit_of_measure` | `str` | `cm\|mm` | 5/5 |
| `fetuses[].measurements[].value` | `float\|int` | `22.62\|6.68\|25\|5.01\|1\|3\|19.12\|5.81\|20.31\|4.14\|...` | 5/5 |
| `fetuses[].ratios` | `list\|null` | - | 5/5 |
| `fetuses[].ratios[]` | `dict` | - | 4/5 |
| `fetuses[].ratios[].calculated_percentile` | `int` | `0` | 4/5 |
| `fetuses[].ratios[].decimal_paces` | `int` | `2\|0` | 4/5 |
| `fetuses[].ratios[].fetus_number` | `int` | `1` | 4/5 |
| `fetuses[].ratios[].label` | `str` | `HC/AC\|FL/AC\|FL/BPD` | 4/5 |
| `fetuses[].ratios[].percentile_for_display` | `str` | - | 4/5 |
| `fetuses[].ratios[].print_in_report` | `int` | `1` | 4/5 |
| `fetuses[].ratios[].range` | `str` | `1.04 - 1.22\|20 - 24\|71 - 87\|1.05 - 1.21\|0.93 - 1.11\|1.05 - 1.22` | 4/5 |
| `fetuses[].ratios[].value` | `float\|int` | `1.105\|22.149\|75\|1.062\|21.653\|71.256\|0.979\|21.424\|74.329\|1.027\|...` | 4/5 |

#### EVMS GE HL7

| viewpoint_path | type | sample | files |
| --- | --- | --- | --- |
| `OBX AbdomenFetus.AbdominalCircumference` | `str (NM)` | `193.7\|145.5\|189.8\|281.3\|218.1\|179` | 6/7 |
| `OBX AbdomenFetus.AbdominalWallAppearance` | `str (ST)` | `normal` | 6/7 |
| `OBX AbdomenFetus.InferiorVenaCavaDiameterZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX AbdomenFetus.VP_AbdominalCircumference_Author` | `str (ST)` | `Hadlock` | 6/7 |
| `OBX AbdomenFetus.VP_AbdominalCircumference_DevRatio` | `str (NM)` | `-1.1\|5\|-3.1\|-1\|-9.5\|-7.1` | 6/7 |
| `OBX AbdomenFetus.VP_AbdominalCircumference_Deviation` | `str (NM)` | `-0.2\|0.5\|-0.5\|-1.7\|-1` | 6/7 |
| `OBX AbdomenFetus.VP_AbdominalCircumference_GA` | `str (NM)` | `169\|139\|166\|225\|184\|159` | 6/7 |
| `OBX AbdomenFetus.VP_AbdominalCircumference_Percentile` | `str (NM)` | `43\|70\|32\|42\|4\|15` | 6/7 |
| `OBX EmbryonicStructuresFetus.CrownRumpLength` | `str (NM)` | `70.7` | 1/7 |
| `OBX EmbryonicStructuresFetus.VP_CrownRumpLength_Author` | `str (ST)` | `Hadlock` | 1/7 |
| `OBX EmbryonicStructuresFetus.VP_CrownRumpLength_DevRatio` | `str (NM)` | `-1.4` | 1/7 |
| `OBX EmbryonicStructuresFetus.VP_CrownRumpLength_Deviation` | `str (NM)` | `-0.1` | 1/7 |
| `OBX EmbryonicStructuresFetus.VP_CrownRumpLength_GA` | `str (NM)` | `93` | 1/7 |
| `OBX EmbryonicStructuresFetus.VP_CrownRumpLength_Percentile` | `str (NM)` | `45` | 1/7 |
| `OBX ExtremitiesFetus.FemurUndefinedLength` | `str (NM)` | `41.1\|25.4\|44.1\|63.2\|48.4\|39` | 6/7 |
| `OBX ExtremitiesFetus.FibulaUndefinedLength` | `str (NM)` | `17.3` | 1/7 |
| `OBX ExtremitiesFetus.HumerusUndefinedLength` | `str (NM)` | `22.5\|44.7` | 2/7 |
| `OBX ExtremitiesFetus.LowerExtremitiesAppearance` | `str (ST)` | `suboptimal\|normal` | 6/7 |
| `OBX ExtremitiesFetus.TibiaUndefinedLength` | `str (NM)` | `17.3` | 1/7 |
| `OBX ExtremitiesFetus.UpperExtremitiesAppearance` | `str (ST)` | `suboptimal\|normal` | 7/7 |
| `OBX ExtremitiesFetus.VP_FemurUndefinedLength_Author` | `str (ST)` | `Hadlock` | 6/7 |
| `OBX ExtremitiesFetus.VP_FemurUndefinedLength_DevRatio` | `str (NM)` | `-6.2\|-15.8\|0.7\|-0.7\|-10.6\|-9.4` | 6/7 |
| `OBX ExtremitiesFetus.VP_FemurUndefinedLength_Deviation` | `str (NM)` | `-0.9\|-1.6\|0.1\|-0.1\|-1.9\|-1.3` | 6/7 |
| `OBX ExtremitiesFetus.VP_FemurUndefinedLength_GA` | `str (NM)` | `163\|124\|172\|229\|184\|158` | 6/7 |
| `OBX ExtremitiesFetus.VP_FemurUndefinedLength_Percentile` | `str (NM)` | `18\|6\|54\|44\|3\|9` | 6/7 |
| `OBX ExtremitiesFetus.VP_FibulaUndefinedLength_Author` | `str (ST)` | `Romero` | 1/7 |
| `OBX ExtremitiesFetus.VP_FibulaUndefinedLength_DevRatio` | `str (NM)` | `-34.2` | 1/7 |
| `OBX ExtremitiesFetus.VP_FibulaUndefinedLength_Deviation` | `str (NM)` | `-2.1` | 1/7 |
| `OBX ExtremitiesFetus.VP_FibulaUndefinedLength_Percentile` | `str (NM)` | `2` | 1/7 |
| `OBX ExtremitiesFetus.VP_HumerusUndefinedLength_Author` | `str (ST)` | `Romero` | 2/7 |
| `OBX ExtremitiesFetus.VP_HumerusUndefinedLength_DevRatio` | `str (NM)` | `-20.5\|-7.4` | 2/7 |
| `OBX ExtremitiesFetus.VP_HumerusUndefinedLength_Deviation` | `str (NM)` | `-1.9\|-1.2` | 2/7 |
| `OBX ExtremitiesFetus.VP_HumerusUndefinedLength_Percentile` | `str (NM)` | `3\|12` | 2/7 |
| `OBX ExtremitiesFetus.VP_TibiaUndefinedLength_Author` | `str (ST)` | `Romero` | 1/7 |
| `OBX ExtremitiesFetus.VP_TibiaUndefinedLength_DevRatio` | `str (NM)` | `-31.6` | 1/7 |
| `OBX ExtremitiesFetus.VP_TibiaUndefinedLength_Deviation` | `str (NM)` | `-2.6` | 1/7 |
| `OBX ExtremitiesFetus.VP_TibiaUndefinedLength_Percentile` | `str (NM)` | `0` | 1/7 |
| `OBX Fetus.BonyThoracicCircumferenceOverAbdominalCircumference` | `str (NM)` | `0.73221477\|0.89056902` | 2/7 |
| `OBX Fetus.EstimatedFetalWeight` | `str (NM)` | `651.85456908\|260.66063565\|679.35773729\|1942.49329768\|918.09260653\|536.32107116` | 6/7 |
| `OBX Fetus.EstimatedFetalWeightLb` | `str (NM)` | `1\|0\|4\|2` | 6/7 |
| `OBX Fetus.EstimatedFetalWeightMethod` | `str (ST)` | `Hadlock (BPD-HC-AC-FL)` | 6/7 |
| `OBX Fetus.EstimatedFetalWeightOz` | `str (NM)` | `7\|9\|8\|5\|0\|3` | 6/7 |
| `OBX Fetus.FemurUndefinedLengthOverAbdominalCircumference` | `str (NM)` | `0.2122\|0.1746\|0.2323\|0.2247\|0.2219\|0.2179` | 6/7 |
| `OBX Fetus.FemurUndefinedLengthOverBiparietalDiameter` | `str (NM)` | `0.5974\|0.6447\|0.6967\|0.8051\|0.7181\|0.7303` | 6/7 |
| `OBX Fetus.FemurUndefinedLengthOverHeadCircumference` | `str (NM)` | `0.18\|0.15\|0.19\|0.22\|0.2\|0.17` | 6/7 |
| `OBX Fetus.HeadCircumferenceOverAbdominalCircumference` | `str (NM)` | `1.16\|1.13\|1.24\|1.04\|1.1\|1.25` | 6/7 |
| `OBX Fetus.VP_EstimatedFetalWeight_DevRatio` | `str (NM)` | `-2.7\|-7.3\|1.4\|-4.9\|-25.6\|-16.3` | 6/7 |
| `OBX Fetus.VP_EstimatedFetalWeight_Deviation` | `str (NM)` | `-0.2\|-0.6\|0.1\|-0.4\|-1.9\|-1.2` | 6/7 |
| `OBX Fetus.VP_EstimatedFetalWeight_Percentile` | `str (NM)` | `42\|29\|54\|36\|3\|11` | 6/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverAbdominalCircumference_Author` | `str (ST)` | `Hadlock` | 6/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverAbdominalCircumference_DevRatio` | `str (NM)` | `-18.1` | 1/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverAbdominalCircumference_Deviation` | `str (NM)` | `-3` | 1/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverAbdominalCircumference_Percentile` | `str (NM)` | `0` | 1/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverBiparietalDiameter_Author` | `str (ST)` | `Hadlock` | 6/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverBiparietalDiameter_DevRatio` | `str (NM)` | `-5.2` | 1/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverBiparietalDiameter_Deviation` | `str (NM)` | `-0.9` | 1/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverBiparietalDiameter_Percentile` | `str (NM)` | `19` | 1/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverHeadCircumference_Author` | `str (ST)` | `Hadlock` | 6/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverHeadCircumference_DevRatio` | `str (NM)` | `-17.3` | 1/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverHeadCircumference_Deviation` | `str (NM)` | `-3.2` | 1/7 |
| `OBX Fetus.VP_FemurUndefinedLengthOverHeadCircumference_Percentile` | `str (NM)` | `0` | 1/7 |
| `OBX Fetus.VP_HeadCircumferenceOverAbdominalCircumference_Author` | `str (ST)` | `Nicolaides` | 6/7 |
| `OBX Fetus.VP_HeadCircumferenceOverAbdominalCircumference_DevRatio` | `str (NM)` | `2\|-4.5\|9\|-1.6\|0.2\|9.6` | 6/7 |
| `OBX Fetus.VP_HeadCircumferenceOverAbdominalCircumference_Deviation` | `str (NM)` | `0.4\|-0.8\|1.6\|-0.3\|0\|1.7` | 6/7 |
| `OBX Fetus.VP_HeadCircumferenceOverAbdominalCircumference_Percentile` | `str (NM)` | `64\|20\|95\|40\|51\|96` | 6/7 |
| `OBX NeckSkinFetus.FetalAnatomyNuchalFoldAppearance` | `str (ST)` | `abnormal` | 1/7 |
| `OBX NeckSkinFetus.NeckAppearance` | `str (ST)` | `abnormal\|normal` | 3/7 |
| `OBX NeckSkinFetus.NeckDetails` | `str (ST)` | `cystic hygroma` | 1/7 |
| `OBX NeckSkinFetus.NuchalFoldThickness` | `str (NM)` | `6.69` | 1/7 |
| `OBX NeckSkinFetus.NuchalTranslucency` | `str (NM)` | `4` | 1/7 |
| `OBX NeckSkinFetus.VP_NuchalTranslucency_Author` | `str (ST)` | `Nicolaides` | 1/7 |
| `OBX NeckSkinFetus.VP_NuchalTranslucency_DevRatio` | `str (NM)` | `110.2` | 1/7 |
| `OBX NeckSkinFetus.VP_NuchalTranslucency_Deviation` | `str (NM)` | `4.5` | 1/7 |
| `OBX NeckSkinFetus.VP_NuchalTranslucency_Percentile` | `str (NM)` | `100` | 1/7 |
| `OBX SkullFetus.BiparietalDiameter` | `str (NM)` | `68.8\|39.4\|63.3\|78.5\|67.4\|53.4` | 6/7 |
| `OBX SkullFetus.BiparietalDiameterOverOccipitoFrontalDiameter` | `str (NM)` | `0.9596\|0.7519\|0.8474\|0.8396\|0.8787\|0.7489` | 6/7 |
| `OBX SkullFetus.HeadAppearance` | `str (ST)` | `abnormal\|normal` | 7/7 |
| `OBX SkullFetus.HeadCircumference` | `str (NM)` | `225.2\|164.5\|234.7\|293.6\|240.9\|224.1` | 6/7 |
| `OBX SkullFetus.HeadDetails` | `str (ST)` | `cloverleaf shape` | 1/7 |
| `OBX SkullFetus.HeadShapeAppearance` | `str (ST)` | `abnormal` | 2/7 |
| `OBX SkullFetus.HeadShapeDetails` | `str (ST)` | `brachycephaly` | 2/7 |
| `OBX SkullFetus.HeadSizeAppearance` | `str (ST)` | `normal` | 1/7 |
| `OBX SkullFetus.OccipitoFrontalDiameter` | `str (NM)` | `71.7\|52.4\|74.7\|93.5\|76.7\|71.3` | 6/7 |
| `OBX SkullFetus.VP_BiparietalDiameterOverOccipitoFrontalDiameter_Author` | `str (ST)` | `Nicolaides` | 6/7 |
| `OBX SkullFetus.VP_BiparietalDiameterOverOccipitoFrontalDiameter_DevRatio` | `str (NM)` | `22.2\|-4.8\|7.9\|5.1\|11.5\|-4.6` | 6/7 |
| `OBX SkullFetus.VP_BiparietalDiameterOverOccipitoFrontalDiameter_Deviation` | `str (NM)` | `4.5\|-1.1\|1.7\|1.1\|2.4` | 6/7 |
| `OBX SkullFetus.VP_BiparietalDiameterOverOccipitoFrontalDiameter_Percentile` | `str (NM)` | `100\|14\|96\|87\|99` | 6/7 |
| `OBX SkullFetus.VP_BiparietalDiameter_Author` | `str (ST)` | `Hadlock` | 6/7 |
| `OBX SkullFetus.VP_BiparietalDiameter_DevRatio` | `str (NM)` | `16.3\|-9.2\|7\|-3.5\|-5.1\|-8.4` | 6/7 |
| `OBX SkullFetus.VP_BiparietalDiameter_Deviation` | `str (NM)` | `3.2\|-1.3\|1.4\|-1\|-1.2\|-1.6` | 6/7 |
| `OBX SkullFetus.VP_BiparietalDiameter_GA` | `str (NM)` | `194\|126\|179\|221\|190\|156` | 6/7 |
| `OBX SkullFetus.VP_BiparietalDiameter_Percentile` | `str (NM)` | `100\|9\|92\|17\|12\|5` | 6/7 |
| `OBX SkullFetus.VP_HeadCircumference_Author` | `str (ST)` | `Chervenak` | 6/7 |
| `OBX SkullFetus.VP_HeadCircumference_DevRatio` | `str (NM)` | `1.9\|6.2\|-2.3\|-8.5\|2.9` | 5/7 |
| `OBX SkullFetus.VP_HeadCircumference_Deviation` | `str (NM)` | `0.3\|0.9\|-0.5\|-1.5\|0.4` | 5/7 |
| `OBX SkullFetus.VP_HeadCircumference_GA` | `str (NM)` | `171\|177\|221\|181\|170` | 5/7 |
| `OBX SkullFetus.VP_HeadCircumference_Percentile` | `str (NM)` | `61\|83\|32\|6\|67` | 5/7 |
| `OBX SkullFetus.VP_OccipitoFrontalDiameter_Author` | `str (ST)` | `Nicolaides` | 6/7 |
| `OBX SkullFetus.VP_OccipitoFrontalDiameter_DevRatio` | `str (NM)` | `-7.1\|-7.6\|-3.3\|-12.7\|-18.1\|-6.2` | 6/7 |
| `OBX SkullFetus.VP_OccipitoFrontalDiameter_Deviation` | `str (NM)` | `-1.5\|-1.6\|-0.7\|-2.8\|-4.1\|-1.3` | 6/7 |
| `OBX SkullFetus.VP_OccipitoFrontalDiameter_GA` | `str (NM)` | `155\|123\|160\|193\|164` | 6/7 |
| `OBX SkullFetus.VP_OccipitoFrontalDiameter_Percentile` | `str (NM)` | `7\|6\|25\|0\|10` | 6/7 |
| `OBX U_FGRData_F_6v65c63705.AbdominalCircumference` | `str (ST)` | `193.7 mm \|145.5 mm , 145.5 mm , 145.5 mm , 145.5 mm \|189.8 mm , 189.8 mm , 189.8 mm \|281.3 mm , 281.3 mm , 281.3 mm \|218.1 mm , 218.1 mm , 218.1 mm \|179 mm , 179 mm , 179 mm , 179 mm ` | 6/7 |
| `OBX U_FGRData_F_6v65c63705.AbdominalCircumferencePercentile` | `str (ST)` | `43% \|70% , 70% , 70% , 70% \|32% , 32% , 32% \|42% , 42% , 42% \|4% , 4% , 4% \|15% , 15% , 15% , 15% ` | 6/7 |
| `OBX U_FGRData_F_6v65c63705.EFW` | `str (ST)` | `652 g \|261 g , 261 g , 261 g , 261 g \|679 g , 679 g , 679 g \|1942 g , 1942 g , 1942 g \|918 g , 918 g , 918 g \|536 g , 536 g , 536 g , 536 g ` | 6/7 |
| `OBX U_FGRData_F_6v65c63705.EFWPercentile` | `str (ST)` | `42% \|29% , 29% , 29% , 29% \|54% , 54% , 54% \|36% , 36% , 36% \|3% , 3% , 3% \|11% , 11% , 11% , 11% ` | 6/7 |
| `OBX U_FGRData_F_6v65c63705.UmbilicalArteryPI` | `str (ST)` | `... \|... , ... , ... , ... \|... , ... , ... \|0.86 , 0.86 , 0.86 ` | 6/7 |
| `OBX U_FGRData_F_6v65c63705.UmbilicalArteryPIPercentile` | `str (ST)` | `... \|... , ... , ... , ... \|... , ... , ... \|9% , 9% , 9% ` | 6/7 |
| `OBX U_FGRData_F_6v65c63705.UmbilicalArteryRI` | `str (ST)` | `... \|... , ... , ... , ... \|... , ... , ... \|0.54 , 0.54 , 0.54 ` | 6/7 |
| `OBX U_FGRData_F_6v65c63705.UmbilicalArteryRIPercentile` | `str (ST)` | `... \|... , ... , ... , ... \|... , ... , ... \|4% , 4% , 4% ` | 6/7 |
| `OBX U_FGRData_F_6v65c63705.UmbilicalArterySD` | `str (ST)` | `... \|... , ... , ... , ... \|... , ... , ... \|2.19 , 2.19 , 2.19 ` | 6/7 |
| `OBX U_FGRData_F_6v65c63705.UmbilicalArterySDPercentile` | `str (ST)` | `... \|... , ... , ... , ... \|... , ... , ... \|7% , 7% , 7% ` | 6/7 |

### cardiac

Fetal cardiac anatomy and echocardiography measurements; heart-specific findings on both sides.

_143 Observer paths, 79 HL7 identifiers._

#### Observer (CUIMC JSON)

| observer_path | type | sample | files |
| --- | --- | --- | --- |
| `fetuses[].dm_echo` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.biventricular_inner_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.biventricular_outer_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.comment` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.comment.formatted_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.comment.plain_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.done` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.inner_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.inner_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.internal_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.internal_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.outer_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.outer_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.root_diameter` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.wall_thickness_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.aortic_root_diameter.wall_thickness_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.biventricular_inner_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.biventricular_outer_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.comment` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.comment.formatted_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.comment.plain_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.done` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.inner_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.inner_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.internal_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.internal_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.outer_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.outer_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.root_diameter` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.wall_thickness_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.biventricular_dimensions.wall_thickness_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.biventricular_inner_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.biventricular_outer_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.comment` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.comment.formatted_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.comment.plain_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.done` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.inner_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.inner_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.internal_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.internal_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.outer_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.outer_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.root_diameter` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.wall_thickness_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.interventricular_septum.wall_thickness_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.left_ventricle.biventricular_inner_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle.biventricular_outer_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle.comment` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.left_ventricle.comment.formatted_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.left_ventricle.comment.plain_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.left_ventricle.done` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle.inner_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle.inner_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle.internal_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle.internal_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle.outer_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle.outer_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle.root_diameter` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle.wall_thickness_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricle.wall_thickness_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.left_ventricular.biventricular_inner_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular.biventricular_outer_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular.comment` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.left_ventricular.comment.formatted_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.left_ventricular.comment.plain_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.left_ventricular.done` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular.inner_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular.inner_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular.internal_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular.internal_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular.outer_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular.outer_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular.root_diameter` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular.wall_thickness_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.left_ventricular.wall_thickness_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.biventricular_inner_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.biventricular_outer_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.comment` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.comment.formatted_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.comment.plain_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.done` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.inner_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.inner_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.internal_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.internal_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.outer_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.outer_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.root_diameter` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.wall_thickness_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.pulmonary_root_diameter.wall_thickness_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.right_ventricle.biventricular_inner_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle.biventricular_outer_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle.comment` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.right_ventricle.comment.formatted_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.right_ventricle.comment.plain_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.right_ventricle.done` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle.inner_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle.inner_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle.internal_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle.internal_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle.outer_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle.outer_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle.root_diameter` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle.wall_thickness_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricle.wall_thickness_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.right_ventricular.biventricular_inner_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular.biventricular_outer_fractional_shortening` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular.comment` | `dict` | - | 5/5 |
| `fetuses[].dm_echo.right_ventricular.comment.formatted_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.right_ventricular.comment.plain_text` | `str` | - | 5/5 |
| `fetuses[].dm_echo.right_ventricular.done` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular.inner_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular.inner_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular.internal_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular.internal_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular.outer_dimension_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular.outer_dimension_systole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular.root_diameter` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular.wall_thickness_diastole` | `int` | `0` | 5/5 |
| `fetuses[].dm_echo.right_ventricular.wall_thickness_systole` | `int` | `0` | 5/5 |
| `fetuses[].fetal_echo_anatomy` | `list` | - | 5/5 |
| `fetuses[].fetal_echo_anatomy[]` | `dict` | - | 5/5 |
| `fetuses[].fetal_echo_anatomy[].anomalies` | `null` | - | 5/5 |
| `fetuses[].fetal_echo_anatomy[].detail` | `null` | - | 5/5 |
| `fetuses[].fetal_echo_anatomy[].main` | `dict` | - | 5/5 |
| `fetuses[].fetal_echo_anatomy[].main.anat_state` | `str` | `Unseen` | 5/5 |
| `fetuses[].fetal_echo_anatomy[].main.label` | `str` | `Visceral/abdominal situs\|4 chamber view apical\|4 chamber view subcostal\|Atrial septum\|Ventricular septum\|LVOT\|RVOT\|3 Vessel-trachea view\|3 Vessel view\|Short Axis ventricles\|...` | 5/5 |
| `fetuses[].fetal_echo_anatomy[].main.main_txt` | `str` | - | 5/5 |
| `fetuses[].fetal_echo_anatomy[].main.print_in_report` | `int` | `0` | 5/5 |
| `fetuses[].fetal_echo_anatomy[].main.required` | `str` | `No` | 5/5 |
| `fetuses[].fetal_echo_measurements` | `null` | - | 5/5 |
| `fetuses[].fetus.heart_bpm` | `int` | `150\|161` | 5/5 |
| `fetuses[].fetus.heart_movement_seen` | `str` | `Seen` | 5/5 |
| `fetuses[].fetus.heart_rate_is` | `str` | `Regular` | 5/5 |

#### EVMS GE HL7

| viewpoint_path | type | sample | files |
| --- | --- | --- | --- |
| `OBX ChestFetus.CardiacAreaOverBonyThoracicArea` | `str (NM)` | `0.28` | 2/7 |
| `OBX ChestFetus.CardiacCircumferenceOverBonyThoracicCircumference` | `str (NM)` | `0.53` | 2/7 |
| `OBX ChestFetus.DuctusArteriosusDiameterZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX ChestFetus.ThoracicDescAortaDetails` | `str (ST)` | `normal` | 2/7 |
| `OBX FetalEchocardiography.AorticArchDetails` | `str (ST)` | `normal` | 2/7 |
| `OBX FetalEchocardiography.DuctusArteriosusDetails` | `str (ST)` | `normal\|forward unaliased flow, normal` | 2/7 |
| `OBX FetalEchocardiography.FetalEchoMarkersOtherFindingsPrint` | `str (ST)` | `Print` | 2/7 |
| `OBX FetalEchocardiography.InferiorVenaCavaDetails` | `str (ST)` | `normal` | 2/7 |
| `OBX FetalEchocardiography.SuperiorVenaCavaDetails` | `str (ST)` | `normal` | 2/7 |
| `OBX FetalEchocardiography.ThymusTTRatioPrint` | `str (ST)` | `Print` | 2/7 |
| `OBX HeartFetus.AortaAscDetails` | `str (ST)` | `normal size and morphology` | 2/7 |
| `OBX HeartFetus.AorticIsthmusDetails` | `str (ST)` | `normal size and morphology` | 2/7 |
| `OBX HeartFetus.AorticIsthmusDiameterZscoreMethod` | `str (ST)` | `Krishnan` | 2/7 |
| `OBX HeartFetus.AorticRootDetails` | `str (ST)` | `aortic root larger than pulmonary root\|normal` | 2/7 |
| `OBX HeartFetus.AorticValveAnnulusDiameterSystole2D` | `str (NM)` | `6.3\|8.5` | 2/7 |
| `OBX HeartFetus.AorticValveAnnulusDiameterSystole2DZscoreBPD` | `str (NM)` | `2.92371661\|5.87769032` | 2/7 |
| `OBX HeartFetus.AorticValveAnnulusDiameterSystole2DZscoreFL` | `str (NM)` | `4.93056572\|7.07297098` | 2/7 |
| `OBX HeartFetus.AorticValveAnnulusDiameterSystole2DZscoreGA` | `str (NM)` | `4.23621336\|6.57253575` | 2/7 |
| `OBX HeartFetus.AorticValveAnnulusDiameterSystole2DZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.AorticValveDetails` | `str (ST)` | `mild aortic regurgitation\|normal size and morphology` | 2/7 |
| `OBX HeartFetus.AorticValveDiameterOverPulmonaryValveDiameterSystole` | `str (NM)` | `0.91970803\|0.82284608` | 2/7 |
| `OBX HeartFetus.AscendingAortaDiameterZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.AtriaDetails` | `str (ST)` | `normal, atria approximately equal in size` | 2/7 |
| `OBX HeartFetus.AtrialSeptumDetails` | `str (ST)` | `normal size and morphology\|aneurysmal flap valve, normal size and morphology` | 2/7 |
| `OBX HeartFetus.AtrioVentricularConnectionsDetails` | `str (ST)` | `common AV junction, balanced ventricles\|concordant, patent AV valves, equal size` | 2/7 |
| `OBX HeartFetus.CardiacActivity` | `str (ST)` | `present` | 7/7 |
| `OBX HeartFetus.CardiacArea` | `str (NM)` | `450.02\|647.73` | 2/7 |
| `OBX HeartFetus.CardiacCircumference` | `str (NM)` | `75.2\|90.22` | 2/7 |
| `OBX HeartFetus.CardiacFunction` | `str (ST)` | `good contractility (normal)\|mildly impaired left ventricular contractility` | 2/7 |
| `OBX HeartFetus.CardiacPosition` | `str (ST)` | `normal` | 1/7 |
| `OBX HeartFetus.CardiacProportions` | `str (ST)` | `proportioned (normal)\|disproportioned` | 2/7 |
| `OBX HeartFetus.CardiacRhythm` | `str (ST)` | `regular (normal)` | 2/7 |
| `OBX HeartFetus.CardiacSize` | `str (ST)` | `normal (approx. 1/3 of thoracic area)\|mildly increased` | 2/7 |
| `OBX HeartFetus.DescendingAortaDiameterZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.FetalHeartRate` | `str (NM)` | `140` | 6/7 |
| `OBX HeartFetus.ForamenOvaleDetails` | `str (ST)` | `normal (in the central third/half, flap valve in left atrium)` | 2/7 |
| `OBX HeartFetus.GreatArteryCrossingDetails` | `str (ST)` | `anterior great artery (confirmed to be the pulmonary artery by its branching) which crosses the course of the proximal aorta, indicative of normal relationship of the great arteries` | 2/7 |
| `OBX HeartFetus.HeartAppearance` | `str (ST)` | `abnormal\|suboptimal\|normal` | 7/7 |
| `OBX HeartFetus.HeartDetails` | `str (ST)` | `Atrioventricular septal defect: Complete\|Ebstein anomaly` | 3/7 |
| `OBX HeartFetus.IntracardiacEchogenicFocusPrint` | `str (ST)` | `Print` | 2/7 |
| `OBX HeartFetus.LeftVentricularAreaZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.LeftVentricularInletDiameterZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.LeftVentricularWidthDiastole2DZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.MVAnnulusOverTVAnnulusDiastole` | `str (NM)` | `1.0813094` | 1/7 |
| `OBX HeartFetus.MitralValveAnnulusDiameterDiastole2D` | `str (NM)` | `10.24` | 1/7 |
| `OBX HeartFetus.MitralValveAnnulusDiameterDiastole2DZscoreBPD` | `str (NM)` | `2.39964631` | 1/7 |
| `OBX HeartFetus.MitralValveAnnulusDiameterDiastole2DZscoreFL` | `str (NM)` | `2.63252498` | 1/7 |
| `OBX HeartFetus.MitralValveAnnulusDiameterDiastole2DZscoreGA` | `str (NM)` | `2.88866451` | 1/7 |
| `OBX HeartFetus.MitralValveAnnulusDiameterDiastole2DZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.MitralValveDetails` | `str (ST)` | `normal size and morphology` | 1/7 |
| `OBX HeartFetus.PericardialEffusion` | `str (ST)` | `no` | 2/7 |
| `OBX HeartFetus.PericardialEffusionPrint` | `str (ST)` | `Print` | 2/7 |
| `OBX HeartFetus.PulmonaryArteryLBranchDiameterZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.PulmonaryArteryLDetails` | `str (ST)` | `normal` | 2/7 |
| `OBX HeartFetus.PulmonaryArteryMainDetails` | `str (ST)` | `normal size and bifurcation` | 2/7 |
| `OBX HeartFetus.PulmonaryArteryMainDiameterZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.PulmonaryArteryRBranchDiameterZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.PulmonaryArteryRDetails` | `str (ST)` | `normal` | 2/7 |
| `OBX HeartFetus.PulmonaryValveAnnulusDiameterSystole2D` | `str (NM)` | `6.85\|10.33` | 2/7 |
| `OBX HeartFetus.PulmonaryValveAnnulusDiameterSystole2DZscoreBPD` | `str (NM)` | `2.24627632\|6.55558603` | 2/7 |
| `OBX HeartFetus.PulmonaryValveAnnulusDiameterSystole2DZscoreFL` | `str (NM)` | `3.9262725\|7.02824005` | 2/7 |
| `OBX HeartFetus.PulmonaryValveAnnulusDiameterSystole2DZscoreGA` | `str (NM)` | `3.63356606\|7.03425837` | 2/7 |
| `OBX HeartFetus.PulmonaryValveAnnulusDiameterSystole2DZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.PulmonaryValveDetails` | `str (ST)` | `pulmonary stenosis\|normal size and morphology` | 2/7 |
| `OBX HeartFetus.PulmonaryVeinsDetails` | `str (ST)` | `normal` | 2/7 |
| `OBX HeartFetus.RightVentricularAreaZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.RightVentricularInletDiameterZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.RightVentricularWidthDiastole2DZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.TricuspidValveAnnulusDiameterDiastole2D` | `str (NM)` | `9.47` | 1/7 |
| `OBX HeartFetus.TricuspidValveAnnulusDiameterDiastole2DZscoreBPD` | `str (NM)` | `1.32092812` | 1/7 |
| `OBX HeartFetus.TricuspidValveAnnulusDiameterDiastole2DZscoreFL` | `str (NM)` | `1.486418` | 1/7 |
| `OBX HeartFetus.TricuspidValveAnnulusDiameterDiastole2DZscoreGA` | `str (NM)` | `1.99539972` | 1/7 |
| `OBX HeartFetus.TricuspidValveAnnulusDiameterDiastole2DZscoreMethod` | `str (ST)` | `Schneider` | 2/7 |
| `OBX HeartFetus.TricuspidValveDetails` | `str (ST)` | `dysplasia, normal size and morphology` | 1/7 |
| `OBX HeartFetus.VenousAtrialConnectionsDetails` | `str (ST)` | `normal` | 2/7 |
| `OBX HeartFetus.VentricleArteryConnectionsDetails` | `str (ST)` | `concordant` | 2/7 |
| `OBX HeartFetus.VentriclesDetails` | `str (ST)` | `normal size and morphology` | 2/7 |
| `OBX HeartFetus.VentricularSeptumDetails` | `str (ST)` | `intact` | 2/7 |
| `OBX HeartFetus.VisceroAtrialSitusAppearance` | `str (ST)` | `situs solitus (normal)` | 2/7 |

### dating

Pregnancy dating: LMP, EDD, gestational age, agreed dating method.

_5 Observer paths, 12 HL7 identifiers._

#### Observer (CUIMC JSON)

| observer_path | type | sample | files |
| --- | --- | --- | --- |
| `exam.age_at_menopause` | `int` | `0` | 5/5 |
| `exam.ga_by_dates` | `int` | `0` | 5/5 |
| `exam.ga_by_working_edd` | `float\|int` | `26.6\|23.6\|35.7\|11\|28` | 5/5 |
| `exam.lmp` | `str` | `0001-01-01` | 5/5 |
| `exam.pt_age_at_edd` | `int` | `45\|44\|43\|42\|41` | 5/5 |

#### EVMS GE HL7

| viewpoint_path | type | sample | files |
| --- | --- | --- | --- |
| `OBX AntenatalBookingHistory.EDDAgreed` | `str (DT)` | `20260113\|20251030\|20250901\|20251001\|20251101` | 7/7 |
| `OBX EpisodeHistory.AgreedDatingString` | `str (ST)` | `based on ultrasound (CRL), selected on 07/10/2025\|based on stated EDD, selected on 07/10/2025` | 7/7 |
| `OBX EpisodeHistory.DefaultLengthofPregnancy` | `str (NM)` | `280` | 7/7 |
| `OBX EpisodeHistory.EDDAgreed` | `str (DT)` | `20260113\|20251030\|20250901\|20251001\|20251101` | 7/7 |
| `OBX EpisodeHistory.EDDbyStatedDating` | `str (DT)` | `20251030\|20250901\|20251001\|20251101` | 4/7 |
| `OBX ExamOBDating.DateOfUltrasoundExamination` | `str (DT)` | `20250923\|20250820\|20250710` | 7/7 |
| `OBX ExamOBDating.EDDCurrentUltrasoundFetus1` | `str (DT)` | `20260107\|20260117\|20260113\|20251024\|20250904\|20251013\|20251106` | 7/7 |
| `OBX ExamOBDating.GestationalAgeDaysAgreed` | `str (NM)` | `168\|134\|93\|227\|197\|166` | 7/7 |
| `OBX ExamOBDating.GestationalAgeDaysStatedDating` | `str (NM)` | `168\|227\|197\|166` | 4/7 |
| `OBX ExamOBDating.GestationalAgeDaysUltrasoundFetus1` | `str (NM)` | `174\|130\|93\|224\|185\|161` | 7/7 |
| `OBX ExamOBDating.MethodOfDating` | `str (ST)` | `based on ultrasound\|based on stated EDD` | 5/7 |
| `OBX ExamOBDating.MethodOfDatingUSIncludedParameterFetus1` | `str (ST)` | `AC, BPD, Femur, HC\|AC, BPD, Femur\|CRL` | 7/7 |

### encounter

Exam-level metadata: date, location, signing, exam type, referring provider, accession, plus GE imaging-parameter and structured-report file blocks.

_30 Observer paths, 34 HL7 identifiers._

#### Observer (CUIMC JSON)

| observer_path | type | sample | files |
| --- | --- | --- | --- |
| `exam` | `dict` | - | 5/5 |
| `exam.accession_id` | `str` | - | 5/5 |
| `exam.disc_perc` | `int` | `0` | 5/5 |
| `exam.examHL7Orders` | `null` | - | 5/5 |
| `exam.examReferring` | `list` | - | 5/5 |
| `exam.examReferring[]` | `dict` | - | 5/5 |
| `exam.examReferring[].assgnd_id` | `int` | `16` | 5/5 |
| `exam.examReferring[].name` | `str` | `Ronald Wapner` | 5/5 |
| `exam.examTypes` | `null` | - | 5/5 |
| `exam.exm_date` | `str` | `2025-07-02\|2025-07-03` | 5/5 |
| `exam.exm_locator` | `str` | `AP10174-U-1-1\|BL10175-U-1-1\|CH10176-U-1-1\|DI10177-U-1-1\|EC10178-U-1-1` | 5/5 |
| `exam.exm_signed` | `int` | `1` | 5/5 |
| `exam.fetus_count` | `int` | `1` | 5/5 |
| `exam.scope_name` | `str` | `Limited OB Exam` | 5/5 |
| `exam.site_name` | `str` | `51 W51st Street` | 5/5 |
| `finalize` | `dict` | - | 5/5 |
| `finalize.attendingMD` | `dict` | - | 5/5 |
| `finalize.attendingMD.assgnd_id` | `int` | `30` | 5/5 |
| `finalize.attendingMD.examiner_no` | `int` | `3` | 5/5 |
| `finalize.attendingMD.name` | `str` | `Ivette Miranda` | 5/5 |
| `finalize.examIcd10Diagnosis` | `null` | - | 5/5 |
| `finalize.examinerTwo` | `dict` | - | 5/5 |
| `finalize.examinerTwo.assgnd_id` | `int` | `30` | 5/5 |
| `finalize.examinerTwo.examiner_no` | `int` | `2` | 5/5 |
| `finalize.examinerTwo.name` | `str` | `Ivette Miranda` | 5/5 |
| `finalize.generalComment` | `dict` | - | 5/5 |
| `finalize.generalComment.formatted_text` | `str` | - | 5/5 |
| `finalize.generalComment.plain_text` | `str` | `The patient was referred for a fetal anatomical survey.  Sonographic measurements were consistent with the expected gestational age. The amniotic fluid volume was normal. A detailed fetal anatomic survey was performed. The sonogram was significant for splaying of the cerebellar hemispheres. There was evidence of a cyst measuring __ connecting with the fourth ventricle. This is consistent with a Dandy-Walker malformation. The remainder of the fetal anatomy seen appeared normal within the resolution of the ultrasound. There was no evidence of macrocephaly, ventriculomegaly or agenesis of the corpus callosum.Due to the limited visualization of the cervix by the transabdominal approach, it was necessary to perform a transvaginal ultrasound. Transvaginal sonogram revealed a long, closed cervix. There were no changes noted with the Valsalva maneuver. A chaperone was present for the transvaginal ultrasound.The patient should be informed of the findings and counseled about the limitations of the exam. Although the absence of any sonographic markers reduces the likelihood of fetal aneuploidy, a normal ultrasound exam cannot exclude abnormal fetal genetics; definitive determination requires diagnostic genetic testing. Thank you for involving us in the care of the patient.\|The patient was referred for a fetal anatomical survey.Sonographic measurements were consistent with the expected gestational age. A detailed fetal anatomic survey was performed and revealed a normal left kidney with a an empty right renal fossa. The right kidney was not visualized and suggest a unilateral renal agenesis.  Color Doppler were used to identified a left renal artery and an absent right renal artery to confirm the diagnosis.  The amniotic fluid was subjectively normal. The rest of the fetal anatomy seen appeared normal within the resolution of the ultrasound. The patient was counseled that this finding has a low risk of anuploidy. There will be a risk of left renal hypertrophy by a compensatory contralateral kidney. She understands that unilateral renal agenesis is associated with Mullerian anomalies in about 40% of  the females with possible unicornuate or bicornuate uterus. Although ultrasound is an effective screening tool, it cannot exclude all congenital anomalies or genetic syndromes. The patient needs a  fetal echo and Pediatric Urology consult. A follow-up ultrasound is advised in 4-6 weeks to reassess fetal growth. Thank you for involving us in the care of the patient.\|The patient was referred for a fetal anatomical survey.  The fetus was appropriately grown and the amniotic fluid volume was normal. An abdominal wall defect consistent with a omphalocele was noted on today's exam.Omphalocele is a condition in which a baby's abdominal organs develop outside their belly. Babies with an omphalocele may also have other health conditions. The exam, however, was limited and all of the anatomical structures could not be satisfactorily visualized.  Due to the limited visualization of the cervix by the transabdominal approach, it was necessary to perform a transvaginal ultrasound. Transvaginal sonogram revealed a long, closed cervix. There were no changes noted with the Valsalva maneuver. A chaperone was present for the transvaginal ultrasound.The patient should be informed of the findings and counseled about the limitations of the exam. Although the absence of any sonographic markers reduces the likelihood of fetal aneuploidy, a normal ultrasound exam cannot exclude abnormal fetal genetics; definitive determination requires diagnostic genetic testing. A follow up exam is recommended prior to 23 weeks to complete the anatomical survey and to increase the detection rate of malformations diagnosed prenatally. Thank you for this referral.\|The patient was seen today for confirmation of pregnancy dating and nuchal translucency measurement. This is an IVF pregnancy with BMI of 33.8Transabdominal sonography was performed and revealed a singleton live intrauterine gestation. Due to limited visualization of the pregnancy transabdominally, a transvaginal exam was performed. The transvaginal exam confirmed the presence of a singleton live intrauterine gestation. Sonographic measurements were consistent with assigned gestational age. A normal fetal heart rate was noted. The amniotic fluid volume appeared normal. Views of the fetal head were suspicious for a cranial anomaly. Specifically, absence of the cranial vault and distortion of the brain is suspected, suggestive of acrania.The uterus and both ovaries were visualized and appeared normal.  No adnexal masses were noted.A follow-up scan is recommended between 11-14 weeks for the nuchal translucency assessment and early anatomy. The patient should also be counseled regarding options for aneuploidy screening and diagnostic testing if not done previously. Thank you for the referral.\|The patient was referred for a fetal anatomical survey.  The fetus was appropriately grown and the amniotic fluid volume was normal. Views of the fetal heart were suspicious for a cardiac anomaly. Specifically, a small ascending aorta, and a small but thick-walled left ventricle and enlarged right heart chambers were visualized.The exam, however, was limited and all of the anatomical structures could not be satisfactorily visualized.  Due to the limited visualization of the cervix by the transabdominal approach, it was necessary to perform a transvaginal ultrasound. Transvaginal sonogram revealed a long, closed cervix. There were no changes noted with the Valsalva maneuver. A chaperone was present for the transvaginal ultrasound.The patient should be informed of the findings and counseled about the limitations of the exam. Although the absence of any sonographic markers reduces the likelihood of fetal aneuploidy, a normal ultrasound exam cannot exclude abnormal fetal genetics; definitive determination requires diagnostic genetic testing. A follow up exam is recommended prior to 23 weeks to complete the anatomical survey and to increase the detection rate of malformations diagnosed prenatally. Thank you for this referral.` | 5/5 |
| `finalize.probes` | `list` | - | 5/5 |
| `finalize.recommendations` | `list` | - | 5/5 |

#### EVMS GE HL7

| viewpoint_path | type | sample | files |
| --- | --- | --- | --- |
| `OBX EpisodeHistory.NumberOfFetuses` | `str (ST)` | `1` | 7/7 |
| `OBX EpisodeHistory.TypeOfGestation` | `str (ST)` | `Singleton pregnancy` | 7/7 |
| `OBX Exam.@@Exam` | `str (NM)` | `18158349\|18157436\|18157386\|18157336\|18157286` | 7/7 |
| `OBX Exam.@@ExamType` | `str (NM)` | `63\|60\|58` | 7/7 |
| `OBX Exam.@@Patient` | `str (NM)` | `600697\|600647\|600597\|600547\|600497` | 7/7 |
| `OBX Exam.@@VPDepartment` | `str (NM)` | `2` | 7/7 |
| `OBX Exam.@Id` | `str (NM)` | `18159164\|18158351\|18158350\|18157437\|18157387\|18157337\|18157287` | 7/7 |
| `OBX Exam.CreatedAt` | `str (TS)` | `20250710155219\|20250710144937\|20250710135410\|20250710135358\|20250710135345\|20250710135333` | 7/7 |
| `OBX Exam.ExamDate` | `str (DT)` | `20250923\|20250820\|20250710` | 7/7 |
| `OBX Exam.ExamTime` | `str (TM)` | `154538\|144800\|144351\|135406\|135352\|135341\|135329` | 7/7 |
| `OBX Exam.Export` | `str (ST)` | `N` | 7/7 |
| `OBX Exam.LangID` | `str (NM)` | `1033` | 7/7 |
| `OBX Exam.Role` | `str (ST)` | `E` | 7/7 |
| `OBX ExamAddData.AgeatExamDate` | `str (NM)` | `24` | 1/7 |
| `OBX ExamAddData.ExamRecommendation` | `str (ST)` | `We recommend a follow up scan only as clinically indicated. \|A fetal echocardiogram is scheduled in 4 weeks.\|A morphology scan is scheduled\|We recommend a follow-up scan only as clinically indicated.` | 7/7 |
| `OBX ExamAddData.ExamState` | `str (ST)` | `Report finalized` | 7/7 |
| `OBX ExamAddData.ExamTitle` | `str (ST)` | `Fetal Echocardiogram\|Detailed Anatomy Assessment\|Detailed First Trimester Anatomy with Nuchal Translucency \|Fetal Echocardiogram with Detailed Anatomy Assessment \|Interval Fetal Growth\|Interval Fetal Growth ` | 7/7 |
| `OBX ExamAddData.Operator1` | `str (ST)` | `Aimee Heeze, RDMS` | 7/7 |
| `OBX ExamAddData.Operator3` | `str (ST)` | `Juliana Gevaerd Martins, M.D.` | 7/7 |
| `OBX ExamAddData.OperatorId3` | `str (NM)` | `96` | 7/7 |
| `OBX ExamContact.@@Contact_ref1` | `str (NM)` | `15894` | 7/7 |
| `OBX ExamContact.@@Listitem` | `str (NM)` | `5545` | 7/7 |
| `OBX ExamStateHistory.@Id` | `str (NM)` | `52213858\|52213859\|56089357\|52212459\|52213857\|56089307\|52212457\|52212458\|56089207\|52210307\|...` | 7/7 |
| `OBX ExamStateHistory.Date` | `str (DT)` | `20250710\|20260410` | 7/7 |
| `OBX ExamStateHistory.NewState` | `str (ST)` | `New exam\|Scan started\|Report finalized` | 7/7 |
| `OBX ExamStateHistory.StationName` | `str (ST)` | `EVMC1LK5Q54\|JEDI1\|EVMCJKH4Q54` | 7/7 |
| `OBX ExamStateHistory.Time` | `str (TM)` | `154538\|154808\|170739\|144800\|151706\|170725\|144351\|144604\|170712\|135406\|...` | 7/7 |
| `OBX ExamStateHistory.UserLoginName` | `str (ST)` | `HeezeAL\|admin` | 7/7 |
| `OBX ImagingParameters.ExamConditions` | `str (ST)` | `Adequate` | 5/7 |
| `OBX ImagingParameters.ImagingProcedure` | `str (ST)` | `Voluson E22, Transabdominal ultrasound examination\|Voluson E22, Transabdominal and transvaginal ultrasound examination\|Voluson E22. Transabdominal ultrasound examination` | 7/7 |
| `OBX VP_MDT_SR_Files.Date` | `str (DT)` | `20250710\|20250717\|20260410` | 7/7 |
| `OBX VP_MDT_SR_Files.Module` | `str (ST)` | `vpmain\|VPMain` | 7/7 |
| `OBX VP_MDT_SR_Files.UID` | `str (ST)` | `1.2.276.0.26.1.1.1.2.2025.227.71280.5185292\|1.2.276.0.26.1.1.1.2.2025.227.69458.2785070\|1.2.276.0.26.1.1.1.2.2025.227.67594.4521521\|1.2.276.0.26.1.1.1.2.2025.227.67300.7632879\|1.2.276.0.26.1.1.1.2.2025.227.67054.4259429\|1.2.276.0.26.1.1.1.2.2025.227.66784.4374300\|1.2.276.0.26.1.1.1.2.2025.227.66530.7405429` | 7/7 |
| `OBX WarningMessage` | `str (ST)` | `Exam contains manually modified mask texts, thus discrete values may be inaccurate.` | 6/7 |

### fetus_core

Per-fetus identity (number, position, presentation, tone, activity), antepartum testing (NST, BPP), and invasive procedures (amniocentesis, FBS/CVS).

_97 Observer paths, 4 HL7 identifiers._

#### Observer (CUIMC JSON)

| observer_path | type | sample | files |
| --- | --- | --- | --- |
| `fetuses` | `list` | - | 5/5 |
| `fetuses[]` | `dict` | - | 5/5 |
| `fetuses[].amniocentesis` | `dict` | - | 5/5 |
| `fetuses[].amniocentesis.amnio_tests` | `list` | - | 5/5 |
| `fetuses[].amniocentesis.amnio_types` | `list` | - | 5/5 |
| `fetuses[].amniocentesis.amniocentesis` | `dict` | - | 5/5 |
| `fetuses[].amniocentesis.amniocentesis.attempts` | `int` | `0` | 5/5 |
| `fetuses[].amniocentesis.amniocentesis.cc_fluid_wd` | `int` | `0` | 5/5 |
| `fetuses[].amniocentesis.amniocentesis.comps` | `str` | `Unspecified` | 5/5 |
| `fetuses[].amniocentesis.amniocentesis.done` | `int` | `0` | 5/5 |
| `fetuses[].amniocentesis.amniocentesis.fluid_char` | `str` | `Unspecified` | 5/5 |
| `fetuses[].amniocentesis.amniocentesis.needle_gauge` | `int` | `0` | 5/5 |
| `fetuses[].amniocentesis.amniocentesis.post_procedure_fetal_heart_motion` | `str` | `Unspecified` | 5/5 |
| `fetuses[].amniocentesis.amniocentesis.post_procedure_rh_factor` | `str` | `Unspecified` | 5/5 |
| `fetuses[].amniocentesis.amniocentesis.post_procedure_rhogam_admin` | `str` | `Unspecified` | 5/5 |
| `fetuses[].amniocentesis.amniocentesis.trans_plac` | `str` | `Unspecified` | 5/5 |
| `fetuses[].amniocentesis.amniocentesis.us_guidance` | `int` | `0` | 5/5 |
| `fetuses[].anatomy` | `list` | - | 5/5 |
| `fetuses[].bpp` | `dict` | - | 5/5 |
| `fetuses[].bpp.afv` | `int` | `0\|2` | 5/5 |
| `fetuses[].bpp.breathing` | `int` | `0\|2` | 5/5 |
| `fetuses[].bpp.mvmnt` | `int` | `0\|2` | 5/5 |
| `fetuses[].bpp.nst` | `int` | `0` | 5/5 |
| `fetuses[].bpp.tone` | `int` | `0\|2` | 5/5 |
| `fetuses[].bpp.total` | `int` | `0\|8` | 5/5 |
| `fetuses[].ectopic_preg` | `dict` | - | 5/5 |
| `fetuses[].ectopic_preg.done` | `int` | `0` | 5/5 |
| `fetuses[].ectopic_preg.ect_loc` | `str` | `Unspecified` | 5/5 |
| `fetuses[].ectopic_preg.ect_size_a` | `int` | `0` | 5/5 |
| `fetuses[].ectopic_preg.ect_size_b` | `int` | `0` | 5/5 |
| `fetuses[].ectopic_preg.ect_size_c` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs` | `dict` | - | 5/5 |
| `fetuses[].fbscvs.cvs` | `dict` | - | 5/5 |
| `fetuses[].fbscvs.cvs.attempts` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.cvs.comps` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fbscvs.cvs.done` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.cvs.mg_of_villi` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.cvs.needle_gauge` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.cvs.trans_abd_cvs` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.cvs.trans_cx_cvs` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.cvs.trans_plac` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fbscvs.cvs.us_guidance` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.cvs.villi_ob` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.cvs_tests` | `list` | - | 5/5 |
| `fetuses[].fbscvs.fetal_blood_sampling` | `dict` | - | 5/5 |
| `fetuses[].fbscvs.fetal_blood_sampling.attempts` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.fetal_blood_sampling.cc_blood_wd` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.fetal_blood_sampling.comps` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fbscvs.fetal_blood_sampling.done` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.fetal_blood_sampling.needle_gauge` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.fetal_blood_sampling.samp_site` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fbscvs.fetal_blood_sampling.samp_site_txt` | `str` | - | 5/5 |
| `fetuses[].fbscvs.fetal_blood_sampling.trans_plac` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fbscvs.fetal_blood_sampling.us_guidance` | `int` | `0` | 5/5 |
| `fetuses[].fbscvs.fetal_blood_sampling_tests` | `list` | - | 5/5 |
| `fetuses[].fetus` | `dict` | - | 5/5 |
| `fetuses[].fetus.anatomy_text` | `str` | `The cerebellum appeared abnormal. Please see anatomy comments for further details. The fetal face appears normal. Anatomy of the fetal thorax appeared within normal limits. The cardiac size and structures appeared sonographically normal at the four chamber view, and cardiac rhythm was regular. The abdominal cavity appears normal. The fetal stomach appears normal. The right kidney appears within normal limits with respect to size, collection systems, and parenchyma. The left kidney appears within normal limits with respect to size, collection systems, and parenchyma. The fetal bladder appears normal. The abdominal wall appears intact. The spine was visualized from cervical to sacral region, within the resolution of the ultrasound equipment, without evidence of a neural tube defect. Active movement of the extremities was seen and fetal body motion was also observed during this examination. Normal genitalia. The placenta appears within normal limits. There is a 3 vessel cord with normal insertion site.\|The fetal cranium appeared normal in shape. The choroid plexus was well visualized, the lateral ventricles were not dilated and the midline structures were not deviated. The cerebellum and cisterna magna were visualized and appeared normal. The fetal face appears normal. Anatomy of the fetal thorax appeared within normal limits. The cardiac size and structures appeared sonographically normal at the four chamber view, and cardiac rhythm was regular. The abdominal cavity appears normal. The fetal stomach appears normal. Abnormalities were noted in the right kidney:  please see the anatomy comments for further details. The left kidney appears within normal limits with respect to size, collection systems, and parenchyma. The fetal bladder appears normal. The abdominal wall appears intact. The spine was visualized from cervical to sacral region, within the resolution of the ultrasound equipment, without evidence of a neural tube defect. Active movement of the extremities was seen and fetal body motion was also observed during this examination. Normal genitalia. The placenta appears within normal limits. There is a 3 vessel cord with normal insertion site.\|The fetal cranium appeared normal in shape. The choroid plexus was well visualized, the lateral ventricles were not dilated and the midline structures were not deviated. The cerebellum and cisterna magna were visualized and appeared normal. The fetal face appears normal. Anatomy of the fetal thorax appeared within normal limits. The cardiac position was not evaluated.         The abdominal cavity appears normal. The fetal stomach appears normal. The right kidney appears within normal limits with respect to size, collection systems, and parenchyma. The left kidney appears within normal limits with respect to size, collection systems, and parenchyma. The fetal bladder appears normal. Abnormal abdominal wall: please see the anatomy comments for further details. The spine was visualized from cervical to sacral region, within the resolution of the ultrasound equipment, without evidence of a neural tube defect. The left forearm appeared normal. The right humerus appeared normal. The left humerus appeared normal. The right forearm appeared normal. The right foot appeared normal. The left foot appeared normal. The right lower leg appeared normal. The left lower leg appeared normal. The right femur appeared normal. The left femur was not evaluated. The right hand appeared normal. The left hand  appeared normal. Normal genitalia. The placenta appears within normal limits. There is a 3 vessel cord with normal insertion site.\|The calvarium was abnormal. Please see anatomy comments for details.\|The fetal cranium appeared normal in shape. The choroid plexus was well visualized, the lateral ventricles were not dilated and the midline structures were not deviated. The cerebellum and cisterna magna were visualized and appeared normal. The fetal face appears normal. Anatomy of the fetal thorax appeared within normal limits. The four chamber view appeared abnormal. Please see anatomy comments for further details.        The abdominal cavity appears normal. The fetal stomach appears normal. The right kidney appears within normal limits with respect to size, collection systems, and parenchyma. The left kidney appears within normal limits with respect to size, collection systems, and parenchyma. The fetal bladder appears normal. The abdominal wall appears intact. The fetal spine was not visualized on today's exam due to fetal position. The fetal extremities were not assessed on today's exam. Normal genitalia. The placenta appears within normal limits. There is a 3 vessel cord with normal insertion site.` | 5/5 |
| `fetuses[].fetus.echo_text` | `str` | - | 5/5 |
| `fetuses[].fetus.estimated_fetal_weight` | `int` | `0` | 5/5 |
| `fetuses[].fetus.fetal_echo_cardiac_axis_degrees` | `int` | `0` | 5/5 |
| `fetuses[].fetus.fetal_echo_performed` | `int` | `0` | 5/5 |
| `fetuses[].fetus.fetus_death` | `int` | `0` | 5/5 |
| `fetuses[].fetus.fetus_growth` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fetus.fetus_number` | `int` | `1` | 5/5 |
| `fetuses[].fetus.fetus_presentation` | `str` | `Vertex\|Breech\|Unspecified` | 5/5 |
| `fetuses[].fetus.fetus_reduced` | `int` | `0` | 5/5 |
| `fetuses[].fetus.fetus_seen` | `int` | `1` | 5/5 |
| `fetuses[].fetus.ga_by_sonography` | `float\|int` | `27\|23.4\|36.1\|11.3\|28.4` | 5/5 |
| `fetuses[].fetus.gender` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fetus.impression_text` | `str` | `Singleton IUPRegular fetal heart rate of 150 bpmAnterior placenta27 weeks and 0 days by this ultrasound. (EDD = OCT 1 2025)26 weeks and 4 days by 1st Trimester Sono. (EDD = OCT 4 2025)Estimated Fetal Weight = 1015 grams Hadlock 85 (AC, FL, HC)Estimated Fetal Weight = 2 lbs 4 oz Hadlock 85 (AC, FL, HC)Dandy Walker\|Singleton IUPRegular fetal heart rate of 150 bpmAnterior placenta23 weeks and 3 days by this ultrasound. (EDD = FEB 16 2026)23 weeks and 4 days by Other. (EDD = OCT 25 2025)Estimated Fetal Weight = 598 grams Hadlock 85 (AC, FL, HC)Estimated Fetal Weight = 1 lbs 5 oz Hadlock 85 (AC, FL, HC)Renal agenesis\|Singleton IUPRegular fetal heart rate of 150 bpmPosterior placenta36 weeks and 1 day by this ultrasound. (EDD = JUL 29 2025)35 weeks and 5 days by Other. (EDD = AUG 1 2025)Estimated Fetal Weight = 2778 grams Hadlock 85 (AC, FL, HC)Estimated Fetal Weight = 6 lbs 2 oz Hadlock 85 (AC, FL, HC)Omphalocele\|Singleton IUPRegular fetal heart rate of 161 bpmPosterior placenta11 weeks and 2 days by this ultrasound. (EDD = JAN 20 2026)11 weeks and 0 days by 1st Trimester Sono. (EDD = JAN 22 2026)Acrania\|Singleton IUPRegular fetal heart rate of 150 bpmPosterior placenta28 weeks and 3 days by this ultrasound. (EDD = SEP 22 2025)28 weeks and 0 days by 2nd Trimester Sono. (EDD = SEP 25 2025)Estimated Fetal Weight = 1274 grams Hadlock 85 (AC, FL, HC)Estimated Fetal Weight = 2 lbs 13 oz Hadlock 85 (AC, FL, HC)Hypoplastic left ventricle` | 5/5 |
| `fetuses[].fetus.multi_fetus_position_anterior_posterior` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fetus.multi_fetus_position_left_right` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fetus.multi_fetus_position_supine` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fetus.use_early_anatomy_text` | `int` | `0` | 5/5 |
| `fetuses[].impression` | `dict` | - | 5/5 |
| `fetuses[].impression.fetus_anomalies` | `list` | - | 5/5 |
| `fetuses[].impression.fetus_anomalies[]` | `dict` | - | 5/5 |
| `fetuses[].impression.fetus_anomalies[].abnom_or_nrml_var` | `int` | `2` | 5/5 |
| `fetuses[].impression.fetus_anomalies[].descr` | `str` | `Dandy Walker\|Renal agenesis\|Omphalocele\|Acrania\|Hypoplastic left ventricle` | 5/5 |
| `fetuses[].impression.fetus_anomalies[].fh_rec_no` | `int` | `451676\|452064\|452450\|452836\|453216` | 5/5 |
| `fetuses[].nst` | `dict` | - | 5/5 |
| `fetuses[].nst.decels_late` | `int` | `0` | 5/5 |
| `fetuses[].nst.decels_pro` | `int` | `0` | 5/5 |
| `fetuses[].nst.decels_var` | `int` | `0` | 5/5 |
| `fetuses[].nst.reactive` | `int` | `0` | 5/5 |
| `fetuses[].nst.spont_hyperstim` | `int` | `0` | 5/5 |
| `fetuses[].nst.time_end` | `str` | - | 5/5 |
| `fetuses[].nst.time_start` | `str` | - | 5/5 |
| `fetuses[].otherprocs` | `dict` | - | 5/5 |
| `fetuses[].otherprocs.fetal_reduction` | `dict` | - | 5/5 |
| `fetuses[].otherprocs.fetal_reduction.done` | `int` | `0` | 5/5 |
| `fetuses[].otherprocs.fetal_reduction.outcome` | `str` | `Unspecified` | 5/5 |
| `fetuses[].otherprocs.fetal_reduction.type` | `str` | `Unspecified` | 5/5 |
| `fetuses[].otherprocs.fetal_transfusion` | `dict` | - | 5/5 |
| `fetuses[].otherprocs.fetal_transfusion.done` | `int` | `0` | 5/5 |
| `fetuses[].otherprocs.fetal_transfusion.success` | `str` | `Unspecified` | 5/5 |
| `fetuses[].otherprocs.fetal_transfusion.type` | `str` | `Unspecified` | 5/5 |

#### EVMS GE HL7

| viewpoint_path | type | sample | files |
| --- | --- | --- | --- |
| `OBX BabyPatientData.Gender` | `str (ST)` | `normal` | 5/7 |
| `OBX Fetus.Identifier` | `str (ST)` | `A` | 7/7 |
| `OBX Fetus.Movements` | `str (ST)` | `movement and tone` | 6/7 |
| `OBX Fetus.Presentation` | `str (ST)` | `transverse \|cephalic\|oblique superior\|transverse` | 6/7 |

### indication_impression

Free-text and coded exam indications, ICD-10 codes, and narrative impressions.

_4 Observer paths, 7 HL7 identifiers._

#### Observer (CUIMC JSON)

| observer_path | type | sample | files |
| --- | --- | --- | --- |
| `exam.examIcd10Indication` | `list` | - | 5/5 |
| `exam.examIcd10Indication[]` | `dict` | - | 5/5 |
| `exam.examIcd10Indication[].code` | `str` | `Z36.1\|O09.529\|O09.519` | 5/5 |
| `exam.examIcd10Indication[].description` | `str` | `Encounter for antenatal screening for raised alphafetoprotein level\|Supervision of elderly multigravida, unspecified trimester\|Supervision of elderly primigravida, unspecified trimester` | 5/5 |

#### EVMS GE HL7

| viewpoint_path | type | sample | files |
| --- | --- | --- | --- |
| `OBX Coding.AutoAcceptanceAlreadyPerformed` | `str (ST)` | `true` | 7/7 |
| `OBX CodingDiagnosis.Code` | `str (ST)` | `Z3A.24\|O76\|O35.9XX0\|Z3A.19\|Z3A.13\|Z36.82\|O35.BXX0\|Z3A.32\|O35.EXX0\|Z3A.28\|...` | 7/7 |
| `OBX CodingDiagnosis.Description` | `str (ST)` | `Weeks of gestation\|Abnormality in fetal heart rate and rhythm complicating labor and delivery\|Maternal care for (suspected) fetal abnormality and damage, unspecified\|Encounter for Nuchal Translucency Screening\|Maternal care for other (suspected) fetal abnormality and damage, fetal cardiac anomalies\|UTD (pyelectasis) found\|Maternal care for known or suspected placental insufficiency` | 7/7 |
| `OBX CodingProcedure.Code` | `str (ST)` | `76816\|76825\|76827\|93325\|76811\|76801\|76813\|76820` | 7/7 |
| `OBX CodingProcedure.Description` | `str (ST)` | `Ultrasound, pregnant uterus, real time with image documentation, follow up, transabdominal approach per fetus\|Echocardiography, fetal, cardiovascular system, real time with image documentation (2D), with or without M-mode recording\|Doppler echocardiography, pulsed wave and/or continuous wave with spectral display; complete\|Doppler echocardiography color flow velocity mapping\|Ultrasound, pregnant uterus, real time with image documentation, fetal and maternal evaluation plus detailed fetal anatomic examination, transabdominal approach;single or first gestation\|Ultrasound, pregnant uterus, real time with image documentation, fetal and maternal evaluation, first trimester (< 14 weeks 0 days), transabdominal approach; single or first gestation\|Ultrasound, pregnant uterus, real time with image documentation, first trimester fetal nuchal translucency measurement, transabdominal or transvaginal approach; single or first gestation\|Doppler velocimetry, fetal; umbilical artery` | 7/7 |
| `OBX ExamAddData.ExamImpression` | `str (ST)` | `The patient is referred for a fetal echocardiogram with multiple anomalies noted.. \.br\\.br\The fetal biometry is consistent with gestational dating derived from her menstrual history. The estimated fetal weight is 652 g at the 42%. Fetal movement and tone are observed. Oligohydramnios is noted with a single deepest pocket of 1.6 cm. \.br\\.br\Multiple anomalies are noted including"\.br\-Abnormal head shape (brachycephaly)\.br\-Bilateral ventriculomegaly\.br\-Major CHD consistent with AVSD and pulmonary stenosis.\.br\\.br\The patient is informed of the findings. She is counseled about the limitations of the exam in detecting all forms of fetal congenital abnormalities. \|The patient is referred for a detailed morphology ultrasound for the detection of fetal anomalies. \.br\\.br\The fetal biometry is consistent with gestational dating derived from her menstrual history. Fetal movement and tone are observed. The amniotic fluid volume appears normal with a single deepest pocket of 2 cm. \.br\\.br\Multiple anomalies are noted including"\.br\-Abnormal head shape (brachycephaly)\.br\-Bilateral ventriculomegaly\.br\-Thickened nuchal fold\.br\-Major CHD consistent with AVSD.\.br\\.br\The patient is informed of the findings. She is counseled about the limitations of the exam in detecting all forms of fetal congenital abnormalities. \|This patient is referred for a detailed first trimester ultrasound for the early detection of fetal anomalies including the nuchal translucency measurement.\.br\ \.br\Transabdominal  images reveal a single intrauterine gestation with positive cardiac activity noted. Fetal crown rump length measurements are consistent with gestational dating derived from today's scan. Fetal movement is noted. The fetal anatomy appears normal for this gestational age; please see comments above for full details. \.br\\.br\A cystic hygroma is noted. The nuchal translucency measures 4 mm at the >99%.\.br\ \.br\The patient is informed of the findings. She is counseled about the limitations of the exam in detecting all forms of fetal congenital abnormalities. \|This patient is referred for a fetal echocardiogram with suspected cardiac anomaly.\.br\\.br\The fetal biometry is consistent with gestational dating derived from her stated EDD. The estimated fetal weight is 679 g at the 54%. The amniotic fluid volume appears normal with a single deepest pocket of 5.4 cm. The fetal anatomy appears normal. \.br\\.br\A 2-vessel umbilical cord is noted.\.br\\.br\Detailed evaluation of fetal cardiac structure and function reveals a major CHD consistent with Ebstein's anomaly; please see comments above for full details.\.br\\.br\The patient is informed of the findings. She is counseled about the limitations of the ultrasound exam in detecting all forms of fetal congenital cardiac abnormalities. \|This patient is referred for interval fetal growth with UTD noted on an outside scan.\.br\\.br\The fetal biometry is consistent with gestational dating derived from her stated EDD. The estimated fetal weight is 1942 g, at the 36%. Fetal movement and tone are observed. The amniotic fluid volume appears normal with a single deepest pocket of 4.6 cm. \.br\\.br\Urinary tract dilation (UTD A2-3) is noted in the right kidney measuring 11.2 mm and in the left kidney measuring 13.4 mm. The renal parenchyma appears normal in size and echogenicity. Normal bladder filling is noted without evidence of ureterocele or ureter dilation. UTD occurs in 1% to 2% of pregnancies and is most commonly a transient finding that is a normal variant. UTD may indicate renal or urinary tract pathology and may also be a marker of Trisomy 21. The association between Trisomy 21 and UTD has been well described in several series, and the finding of UTD confers a positive LR of 1.5, suggesting a minimal risk. For pregnant patients with negative serum or cfDNA screening results and isolated UTD, we recommend no further aneuploidy evaluation. For fetuses with isolated UTD A1, we recommend an ultrasound examination at about 32 weeks of gestation and pediatric urology consultation. For fetuses with UTD A2-3, we recommend ultrasound assessment every 4-6 weeks and pediatric urology. \.br\\.br\The patient is informed of the findings. She is counseled about the limitations of the ultrasound exam in detecting all forms of fetal congenital cardiac abnormalities. \|This patient is referred for interval fetal growth with FGR.\.br\\.br\The fetal biometry is consistent with gestational dating derived from her stated EDD. The estimated fetal weight is 918 g, at the 3%. Fetal movement and tone are observed. The amniotic fluid volume appears normal with a single deepest pocket of 3.4 cm. \.br\\.br\Doppler velocimetry evaluation of the umbilical artery is within normal limits for this gestational age. \.br\\.br\The patient is informed of the findings. She is counseled about the limitations of the ultrasound exam in detecting all forms of fetal congenital cardiac abnormalities. \|The patient is referred for a detailed morphology ultrasound for the detection of fetal anomalies. \.br\\.br\The fetal biometry is consistent with gestational dating derived from her menstrual history. Fetal movement and tone are observed. The amniotic fluid volume appears normal with a single deepest pocket of 4.3 cm. \.br\\.br\Today's findings include:\.br\- Abnormal skull shape (cloverleaf)\.br\- Right lateral ventriculomegaly\.br\- Hypoplasia of the cerebellum\.br\\.br\The patient is informed of the findings. She is counseled about the limitations of the exam in detecting all forms of fetal congenital abnormalities. ` | 7/7 |
| `OBX ExamCodingIndication.Indication` | `str (ST)` | `Known or suspected fetal anomaly\|Fetal Distress, Known or Suspected\|Encounter for Nuchal Translucency Screening\|Known fetal cardiac abnormality\|UTD (pyelectasis) found\|Fetal Growth Restriction` | 7/7 |

### maternal_subject

Maternal demographics and history: patient block, obstetric history, family/anamnestic history, antenatal booking, screening tests.

_31 Observer paths, 11 HL7 identifiers._

#### Observer (CUIMC JSON)

| observer_path | type | sample | files |
| --- | --- | --- | --- |
| `exam.ob_gyn_history` | `dict` | - | 5/5 |
| `exam.ob_gyn_history.ect_preg_num_left` | `int` | `0` | 5/5 |
| `exam.ob_gyn_history.ect_preg_num_other` | `int` | `0` | 5/5 |
| `exam.ob_gyn_history.ect_preg_num_right` | `int` | `0` | 5/5 |
| `exam.ob_gyn_history.f_term` | `int` | `0` | 5/5 |
| `exam.ob_gyn_history.gravida` | `int` | `0` | 5/5 |
| `exam.ob_gyn_history.liv_children` | `int` | `0` | 5/5 |
| `exam.ob_gyn_history.p_term` | `int` | `0` | 5/5 |
| `exam.ob_gyn_history.para` | `int` | `0` | 5/5 |
| `exam.ob_gyn_history.s_abort` | `int` | `0` | 5/5 |
| `exam.ob_gyn_history.stl_born` | `int` | `0` | 5/5 |
| `exam.ob_gyn_history.t_abort` | `int` | `0` | 5/5 |
| `exam.patient` | `dict` | - | 5/5 |
| `exam.patient.b_date` | `str` | `1980-04-01\|1981-05-02\|1982-06-03\|1983-07-04\|1984-08-05` | 5/5 |
| `exam.patient.first_name` | `str` | `Sally` | 5/5 |
| `exam.patient.last_name` | `str` | `Apple\|Blue\|Charm\|Diva\|Eclair` | 5/5 |
| `exam.pt_age_at_exam` | `int` | `45\|44\|43\|41\|40` | 5/5 |
| `hist_phys_vitals` | `dict` | - | 5/5 |
| `hist_phys_vitals.surgeries` | `null` | - | 5/5 |
| `hist_phys_vitals.vital_signs` | `dict` | - | 5/5 |
| `hist_phys_vitals.vital_signs.bmi` | `float\|int` | `0\|25\|29.3` | 5/5 |
| `hist_phys_vitals.vital_signs.height_feet` | `int` | `0\|5` | 5/5 |
| `hist_phys_vitals.vital_signs.height_inches` | `int` | `0\|5\|7` | 5/5 |
| `hist_phys_vitals.vital_signs.initial_blood_pressure_dia` | `int` | `0` | 5/5 |
| `hist_phys_vitals.vital_signs.initial_blood_pressure_sys` | `int` | `0` | 5/5 |
| `hist_phys_vitals.vital_signs.initial_plood_uressurelse` | `int` | `0` | 5/5 |
| `hist_phys_vitals.vital_signs.later_bp_dia` | `int` | `0` | 5/5 |
| `hist_phys_vitals.vital_signs.later_bp_sys` | `int` | `0` | 5/5 |
| `hist_phys_vitals.vital_signs.later_pulse` | `int` | `0` | 5/5 |
| `hist_phys_vitals.vital_signs.time_vitals_rec_init` | `str` | - | 5/5 |
| `hist_phys_vitals.vital_signs.weight_lb` | `int` | `0\|150\|187` | 5/5 |

#### EVMS GE HL7

| viewpoint_path | type | sample | files |
| --- | --- | --- | --- |
| `OBX MaternalScreeningTests.Print` | `str (ST)` | `Print` | 7/7 |
| `OBX PatientAnamnesticData.Gravida` | `str (NM)` | `1` | 7/7 |
| `OBX PatientAnamnesticData.Para` | `str (NM)` | `0` | 7/7 |
| `OBX PatientFamilyHistory.PatientFamilyHistoryDetails` | `str (ST)` | `spina bifida` | 1/7 |
| `OBX PatientFamilyHistory.Print` | `str (ST)` | `Print` | 1/7 |
| `OBX PatientFamilyHistory.RelativeHistory` | `str (ST)` | `Father` | 1/7 |
| `OBX PatientHistory.Country` | `str (ST)` | `USA` | 7/7 |
| `OBX PatientHistory.DOB` | `str (DT)` | `20010101` | 1/7 |
| `OBX PatientHistory.FirstName` | `str (ST)` | `Test5\|Test4\|Test3\|Test2\|Test1` | 7/7 |
| `OBX PatientHistory.Name` | `str (ST)` | `Phenotype` | 7/7 |
| `OBX PatientHistory.Sex` | `str (ST)` | `unknown` | 7/7 |

### non_fetal_gyn

Non-fetal gynecologic anatomy: adnexa, cervix, endomyometrial / uterine findings, uterine artery Doppler, gynecologic procedures.

_243 Observer paths, 4 HL7 identifiers._

#### Observer (CUIMC JSON)

| observer_path | type | sample | files |
| --- | --- | --- | --- |
| `adnexa` | `dict` | - | 5/5 |
| `adnexa.left` | `dict` | - | 5/5 |
| `adnexa.left.done` | `int` | `0` | 5/5 |
| `adnexa.left.ovry_loc` | `str` | `Unspecified` | 5/5 |
| `adnexa.left.ovry_seen` | `str` | `Unspecified` | 5/5 |
| `adnexa.left.ovry_size_a` | `int` | `0` | 5/5 |
| `adnexa.left.ovry_size_b` | `int` | `0` | 5/5 |
| `adnexa.left.ovry_size_c` | `int` | `0` | 5/5 |
| `adnexa.left.ovry_surg_abs` | `int` | `0` | 5/5 |
| `adnexa.left.ovry_vol` | `int` | `0` | 5/5 |
| `adnexa.left.tube_hydrosalpinx` | `int` | `0` | 5/5 |
| `adnexa.left.tube_hydrosalpinx_size_a` | `int` | `0` | 5/5 |
| `adnexa.left.tube_hydrosalpinx_size_b` | `int` | `0` | 5/5 |
| `adnexa.left.tube_hydrosalpinx_size_c` | `int` | `0` | 5/5 |
| `adnexa.left.tube_hydrosalpinx_volume` | `int` | `0` | 5/5 |
| `adnexa.left.tube_nrml` | `str` | `Unspecified` | 5/5 |
| `adnexa.left.tube_seen` | `str` | `Unspecified` | 5/5 |
| `adnexa.left.tube_surg_abs` | `int` | `0` | 5/5 |
| `adnexa.masses` | `null` | - | 5/5 |
| `adnexa.right` | `dict` | - | 5/5 |
| `adnexa.right.done` | `int` | `0` | 5/5 |
| `adnexa.right.ovry_loc` | `str` | `Unspecified` | 5/5 |
| `adnexa.right.ovry_seen` | `str` | `Unspecified` | 5/5 |
| `adnexa.right.ovry_size_a` | `int` | `0` | 5/5 |
| `adnexa.right.ovry_size_b` | `int` | `0` | 5/5 |
| `adnexa.right.ovry_size_c` | `int` | `0` | 5/5 |
| `adnexa.right.ovry_surg_abs` | `int` | `0` | 5/5 |
| `adnexa.right.ovry_vol` | `int` | `0` | 5/5 |
| `adnexa.right.tube_hydrosalpinx` | `int` | `0` | 5/5 |
| `adnexa.right.tube_hydrosalpinx_size_a` | `int` | `0` | 5/5 |
| `adnexa.right.tube_hydrosalpinx_size_b` | `int` | `0` | 5/5 |
| `adnexa.right.tube_hydrosalpinx_size_c` | `int` | `0` | 5/5 |
| `adnexa.right.tube_hydrosalpinx_volume` | `int` | `0` | 5/5 |
| `adnexa.right.tube_nrml` | `str` | `Unspecified` | 5/5 |
| `adnexa.right.tube_seen` | `str` | `Unspecified` | 5/5 |
| `adnexa.right.tube_surg_abs` | `int` | `0` | 5/5 |
| `cervix` | `dict` | - | 5/5 |
| `cervix.cervix` | `dict` | - | 5/5 |
| `cervix.cervix.cecrlage_elective` | `int` | `0` | 5/5 |
| `cervix.cervix.cecrlage_emergency` | `int` | `0` | 5/5 |
| `cervix.cervix.cecrlage_ga_placement` | `int` | `0` | 5/5 |
| `cervix.cervix.cecrlage_lower_cx_post_tfp` | `int` | `0` | 5/5 |
| `cervix.cervix.cecrlage_lower_cx_standing` | `int` | `0` | 5/5 |
| `cervix.cervix.cecrlage_lower_cx_supine` | `int` | `0` | 5/5 |
| `cervix.cervix.cecrlage_mcdonald` | `int` | `0` | 5/5 |
| `cervix.cervix.cecrlage_shirodkar` | `int` | `0` | 5/5 |
| `cervix.cervix.cecrlage_upper_cx_post_tfp` | `int` | `0` | 5/5 |
| `cervix.cervix.cecrlage_upper_cx_standing` | `int` | `0` | 5/5 |
| `cervix.cervix.cecrlage_upper_cx_supine` | `int` | `0` | 5/5 |
| `cervix.cervix.cervicx_length_post_tfp` | `int` | `0` | 5/5 |
| `cervix.cervix.cervicx_length_standing` | `int` | `0` | 5/5 |
| `cervix.cervix.cervicx_length_supine` | `float\|int` | `0\|3.5` | 5/5 |
| `cervix.cervix.dilation` | `int` | `0` | 5/5 |
| `cervix.cervix.done` | `int` | `1\|0` | 5/5 |
| `cervix.cervix.dynamic_chngs` | `str` | `Unspecified` | 5/5 |
| `cervix.cervix.exam_performed_by_us` | `int` | `0` | 5/5 |
| `cervix.cervix.exam_performed_manually` | `int` | `0` | 5/5 |
| `cervix.cervix.funneling` | `str` | `Unspecified` | 5/5 |
| `cervix.cervix.funneling_lngth_post_tfp` | `int` | `0` | 5/5 |
| `cervix.cervix.funneling_lngth_standing` | `int` | `0` | 5/5 |
| `cervix.cervix.funneling_lngth_supine` | `int` | `0` | 5/5 |
| `cervix.cervix.funneling_percent_post_tfp` | `int` | `0` | 5/5 |
| `cervix.cervix.funneling_percent_standing` | `int` | `0` | 5/5 |
| `cervix.cervix.funneling_percent_supine` | `int` | `0` | 5/5 |
| `cervix.cervix.funneling_width_post_tfp` | `int` | `0` | 5/5 |
| `cervix.cervix.funneling_width_standing` | `int` | `0` | 5/5 |
| `cervix.cervix.funneling_width_supine` | `int` | `0` | 5/5 |
| `cervix.cervix.int_os_to_ext_os_post_tfp` | `int` | `0` | 5/5 |
| `cervix.cervix.int_os_to_ext_os_standing` | `int` | `0` | 5/5 |
| `cervix.cervix.int_os_to_ext_os_supine` | `int` | `0` | 5/5 |
| `cervix.cervix.length` | `int` | `0` | 5/5 |
| `cervix.cervix.normal` | `str` | `Normal\|Unspecified` | 5/5 |
| `cervix.cervix.response_to_standing` | `str` | `Unspecified` | 5/5 |
| `cervix.cervix.response_to_tfp` | `str` | `Unspecified` | 5/5 |
| `cervix.cervix.response_to_tfp_debris` | `str` | `Unspecified` | 5/5 |
| `cervix.cervix.response_to_valsalva` | `str` | `Unspecified` | 5/5 |
| `cervix.cervix.surg_abs` | `int` | `0` | 5/5 |
| `cervix.cervix_anomalies` | `null` | - | 5/5 |
| `endomyocds` | `dict` | - | 5/5 |
| `endomyocds.endo_contents` | `null` | - | 5/5 |
| `endomyocds.gyn_anomalies` | `null` | - | 5/5 |
| `endomyocds.gyn_data` | `dict` | - | 5/5 |
| `endomyocds.gyn_data.cds_fld_amt` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.cds_fld_descr` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.cds_fld_other_txt` | `str` | - | 5/5 |
| `endomyocds.gyn_data.cds_fld_seen` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.cds_fld_size_a` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.cds_fld_size_b` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.cds_fld_size_c` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.cds_fld_volume` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.done` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.endo_colr_dop` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.endo_cont_fld_pres` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.endo_cont_fld_type` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.endo_cont_other_txt` | `str` | - | 5/5 |
| `endomyocds.gyn_data.endo_dop_ri` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.endo_dop_ri_value` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.endo_lining` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.endo_shape` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.endo_thickness_cm` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.endo_thickness_layers` | `int` | `0` | 5/5 |
| `endomyocds.gyn_data.gen_comment` | `str` | - | 5/5 |
| `endomyocds.gyn_data.myo_homo_hetro` | `int` | `0` | 5/5 |
| `gyn_procedure` | `dict` | - | 5/5 |
| `gyn_procedure.gyn_procedure` | `dict` | - | 5/5 |
| `gyn_procedure.gyn_procedure.done` | `int` | `0` | 5/5 |
| `gyn_procedure.gyn_procedure.hysteroscopy_amt` | `int` | `0` | 5/5 |
| `gyn_procedure.gyn_procedure.hysteroscopy_done` | `int` | `0` | 5/5 |
| `gyn_procedure.gyn_procedure.hysteroscopy_fld_type` | `str` | - | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystgrpy_amt` | `int` | `0` | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystgrpy_cath_type` | `str` | `Unspecified` | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystgrpy_cath_type_txt` | `str` | - | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystgrpy_done` | `int` | `0` | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystgrpy_fld_type` | `str` | `Unspecified` | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystgrpy_fld_type_txt` | `str` | - | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystgrpy_nrml` | `int` | `0` | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystsalgrpy_l_tube_fld_oth` | `str` | - | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystsalgrpy_lft_tube` | `str` | `Unspecified` | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystsalgrpy_lft_tube_blk` | `str` | `Unspecified` | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystsalgrpy_lft_tube_fld` | `int` | `0` | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystsalgrpy_r_tube_fld_oth` | `str` | - | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystsalgrpy_rht_tube` | `str` | `Unspecified` | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystsalgrpy_rht_tube_blk` | `str` | `Unspecified` | 5/5 |
| `gyn_procedure.gyn_procedure.sonohystsalgrpy_rht_tube_fld` | `int` | `0` | 5/5 |
| `gyn_procedure.hormone_replacement_therapy` | `null` | - | 5/5 |
| `uterine_artery` | `dict` | - | 5/5 |
| `uterine_artery.left` | `dict` | - | 5/5 |
| `uterine_artery.left.a_over_i` | `int` | `0` | 5/5 |
| `uterine_artery.left.a_over_i_pc` | `int` | `0` | 5/5 |
| `uterine_artery.left.aedv` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.left.at` | `int` | `0` | 5/5 |
| `uterine_artery.left.at_pc` | `int` | `0` | 5/5 |
| `uterine_artery.left.dominant` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.left.done` | `int` | `0` | 5/5 |
| `uterine_artery.left.notch` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.left.notch_depth` | `int` | `0` | 5/5 |
| `uterine_artery.left.pi` | `int` | `0` | 5/5 |
| `uterine_artery.left.pi_pc` | `int` | `0` | 5/5 |
| `uterine_artery.left.psv` | `int` | `0` | 5/5 |
| `uterine_artery.left.psv_pc` | `int` | `0` | 5/5 |
| `uterine_artery.left.rev_flow` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.left.ri` | `int` | `0` | 5/5 |
| `uterine_artery.left.ri_pc` | `int` | `0` | 5/5 |
| `uterine_artery.left.sd` | `int` | `0` | 5/5 |
| `uterine_artery.left.sd_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left` | `dict` | - | 5/5 |
| `uterine_artery.postpartum_left.a_over_i` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.a_over_i_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.aedv` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.postpartum_left.at` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.at_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.dominant` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.postpartum_left.done` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.notch` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.postpartum_left.notch_depth` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.pi` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.pi_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.psv` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.psv_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.rev_flow` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.postpartum_left.ri` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.ri_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.sd` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_left.sd_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right` | `dict` | - | 5/5 |
| `uterine_artery.postpartum_right.a_over_i` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.a_over_i_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.aedv` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.postpartum_right.at` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.at_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.dominant` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.postpartum_right.done` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.notch` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.postpartum_right.notch_depth` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.pi` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.pi_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.psv` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.psv_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.rev_flow` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.postpartum_right.ri` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.ri_pc` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.sd` | `int` | `0` | 5/5 |
| `uterine_artery.postpartum_right.sd_pc` | `int` | `0` | 5/5 |
| `uterine_artery.right` | `dict` | - | 5/5 |
| `uterine_artery.right.a_over_i` | `int` | `0` | 5/5 |
| `uterine_artery.right.a_over_i_pc` | `int` | `0` | 5/5 |
| `uterine_artery.right.aedv` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.right.at` | `int` | `0` | 5/5 |
| `uterine_artery.right.at_pc` | `int` | `0` | 5/5 |
| `uterine_artery.right.dominant` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.right.done` | `int` | `0` | 5/5 |
| `uterine_artery.right.notch` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.right.notch_depth` | `int` | `0` | 5/5 |
| `uterine_artery.right.pi` | `int` | `0` | 5/5 |
| `uterine_artery.right.pi_pc` | `int` | `0` | 5/5 |
| `uterine_artery.right.psv` | `int` | `0` | 5/5 |
| `uterine_artery.right.psv_pc` | `int` | `0` | 5/5 |
| `uterine_artery.right.rev_flow` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.right.ri` | `int` | `0` | 5/5 |
| `uterine_artery.right.ri_pc` | `int` | `0` | 5/5 |
| `uterine_artery.right.sd` | `int` | `0` | 5/5 |
| `uterine_artery.right.sd_pc` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental` | `dict` | - | 5/5 |
| `uterine_artery.subplacental.a_over_i` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.a_over_i_pc` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.aedv` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.subplacental.at` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.at_pc` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.dominant` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.subplacental.done` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.notch` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.subplacental.notch_depth` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.pi` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.pi_pc` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.psv` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.psv_pc` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.rev_flow` | `str` | `Unspecified` | 5/5 |
| `uterine_artery.subplacental.ri` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.ri_pc` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.sd` | `int` | `0` | 5/5 |
| `uterine_artery.subplacental.sd_pc` | `int` | `0` | 5/5 |
| `uterus` | `dict` | - | 5/5 |
| `uterus.bladder` | `dict` | - | 5/5 |
| `uterus.bladder.contours` | `str` | `Unspecified` | 5/5 |
| `uterus.bladder.description` | `str` | `Unspecified` | 5/5 |
| `uterus.bladder.done` | `int` | `0` | 5/5 |
| `uterus.uterus` | `dict` | - | 5/5 |
| `uterus.uterus.anteflexed` | `int` | `0` | 5/5 |
| `uterus.uterus.anteverted` | `int` | `0` | 5/5 |
| `uterus.uterus.dextroverted` | `int` | `0` | 5/5 |
| `uterus.uterus.done` | `int` | `1\|0` | 5/5 |
| `uterus.uterus.levoverted` | `int` | `0` | 5/5 |
| `uterus.uterus.midplane` | `int` | `0` | 5/5 |
| `uterus.uterus.qual_size` | `str` | `Unspecified` | 5/5 |
| `uterus.uterus.retroflexed` | `int` | `0` | 5/5 |
| `uterus.uterus.retroverted` | `int` | `0` | 5/5 |
| `uterus.uterus.seen` | `str` | `Visualized\|Unspecified` | 5/5 |
| `uterus.uterus.shape` | `str` | `Unspecified` | 5/5 |
| `uterus.uterus.size_a` | `int` | `0` | 5/5 |
| `uterus.uterus.size_b` | `int` | `0` | 5/5 |
| `uterus.uterus.size_c` | `int` | `0` | 5/5 |
| `uterus.uterus.surgically_absent` | `int` | `0` | 5/5 |
| `uterus.uterus_anomalies` | `null` | - | 5/5 |

#### EVMS GE HL7

| viewpoint_path | type | sample | files |
| --- | --- | --- | --- |
| `OBX Cervix.Appearance` | `str (ST)` | `Visualized` | 2/7 |
| `OBX Cervix.ApproachCervicalBiometry` | `str (ST)` | `Transvaginal with valsalva` | 2/7 |
| `OBX Cervix.FunnellingYN` | `str (ST)` | `Funneling absent` | 2/7 |
| `OBX Cervix.OtherFindings` | `str (ST)` | `normal` | 2/7 |

### placenta_cord

Placenta location and grading, umbilical cord findings, umbilical artery Doppler indices, and fetal-vessel data.

_133 Observer paths, 32 HL7 identifiers._

#### Observer (CUIMC JSON)

| observer_path | type | sample | files |
| --- | --- | --- | --- |
| `fetuses[].fetalvessels` | `dict` | - | 5/5 |
| `fetuses[].fetalvessels.ductus_venosus` | `dict` | - | 5/5 |
| `fetuses[].fetalvessels.ductus_venosus.done` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.ductus_venosus.ductus_venosus_index` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.ductus_venosus.peak_atrial_systolic` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.ductus_venosus.peak_ventricular_diastolic` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.ductus_venosus.peak_ventricular_systolic` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.ductus_venosus.reverse_flow` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fetalvessels.ductus_venosus.systolic_atrial_ratio` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.ductus_venosus.systolic_diastolic_ratio` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.intrahep_vein` | `dict` | - | 5/5 |
| `fetuses[].fetalvessels.intrahep_vein.done` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.intrahep_vein.pulsations` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery` | `dict` | - | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.absent_end_diastolic_velocity` | `str` | `?` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.done` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.peak_systolic_velocity` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.peak_systolic_velocity_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.peak_systolic_velocity_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.peak_systolic_velocity_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.pulsatility_index` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.pulsatility_index_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.pulsatility_index_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.pulsatility_index_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.resistance_index` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.resistance_index_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.resistance_index_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.resistance_index_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.systolic_diastolic_ratio` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.systolic_diastolic_ratio_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.systolic_diastolic_ratio_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.middle_cerebral_artery.systolic_diastolic_ratio_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery` | `dict` | - | 5/5 |
| `fetuses[].fetalvessels.renal_artery.done` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.pulsatility_index` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.pulsatility_index_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.pulsatility_index_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.pulsatility_index_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.resistance_index` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.resistance_index_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.resistance_index_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.resistance_index_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.systolic_diastolic_ratio` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.systolic_diastolic_ratio_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.systolic_diastolic_ratio_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.renal_artery.systolic_diastolic_ratio_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta` | `dict` | - | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.absent_end_diastolic_velocity` | `str` | `?` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.done` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.peak_systolic_velocity` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.peak_systolic_velocity_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.peak_systolic_velocity_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.peak_systolic_velocity_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.pulsatility_index` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.pulsatility_index_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.pulsatility_index_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.pulsatility_index_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.resistance_index` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.resistance_index_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.resistance_index_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.resistance_index_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.reverse_flow` | `str` | `?` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.systolic_diastolic_ratio` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.systolic_diastolic_ratio_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.systolic_diastolic_ratio_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.thoracic_aorta.systolic_diastolic_ratio_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery` | `dict` | - | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.absent_end_diastolic_velocity` | `str` | `?` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.done` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.pulsatility_index` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.pulsatility_index_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.pulsatility_index_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.pulsatility_index_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.resistance_index` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.resistance_index_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.resistance_index_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.resistance_index_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.reverse_flow` | `str` | `?` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.systolic_diastolic_ratio` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.systolic_diastolic_ratio_mom` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.systolic_diastolic_ratio_percentile` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_artery.systolic_diastolic_ratio_z_score` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_vein` | `dict` | - | 5/5 |
| `fetuses[].fetalvessels.umbilical_vein.done` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.umbilical_vein.pulsations` | `str` | `Unspecified` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_inferior` | `dict` | - | 5/5 |
| `fetuses[].fetalvessels.vena_cava_inferior.atrial_filling_index` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_inferior.done` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_inferior.peak_diastolic_flow` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_inferior.peak_reverse_flow` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_inferior.pi_reverse_over_pi_forward_ratio` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_inferior.pulsatility_index_forward` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_inferior.pulsatility_index_reverse` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_inferior.systolic_velocity_max` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_inferior.systolic_velocity_min` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_inferior.velocity_time_integral_systolic_wave` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_superior` | `dict` | - | 5/5 |
| `fetuses[].fetalvessels.vena_cava_superior.atrial_filling_index` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_superior.done` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_superior.peak_diastolic_flow` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_superior.peak_reverse_flow` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_superior.pi_reverse_over_pi_forward_ratio` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_superior.pulsatility_index_forward` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_superior.pulsatility_index_reverse` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_superior.systolic_velocity_max` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_superior.systolic_velocity_min` | `int` | `0` | 5/5 |
| `fetuses[].fetalvessels.vena_cava_superior.velocity_time_integral_systolic_wave` | `int` | `0` | 5/5 |
| `fetuses[].placenta` | `dict` | - | 5/5 |
| `fetuses[].placenta.amnion_seen` | `str` | `Unspecified\|Seen` | 5/5 |
| `fetuses[].placenta.anterior_pos` | `int` | `1\|0` | 5/5 |
| `fetuses[].placenta.chor_amniotic` | `str` | `Unspecified` | 5/5 |
| `fetuses[].placenta.chor_chorionic` | `str` | `Unspecified` | 5/5 |
| `fetuses[].placenta.done` | `int` | `1` | 5/5 |
| `fetuses[].placenta.echoluc` | `str` | `Unspecified` | 5/5 |
| `fetuses[].placenta.fundal_pos` | `int` | `0` | 5/5 |
| `fetuses[].placenta.grade` | `str` | `Unspecified` | 5/5 |
| `fetuses[].placenta.lft_lat_pos` | `int` | `0` | 5/5 |
| `fetuses[].placenta.low_lyng_pos` | `int` | `0` | 5/5 |
| `fetuses[].placenta.posterior_pos` | `int` | `0\|1` | 5/5 |
| `fetuses[].placenta.previa` | `str` | `Unspecified` | 5/5 |
| `fetuses[].placenta.rht_lat_pos` | `int` | `0` | 5/5 |
| `fetuses[].placenta.subchor_sonoluc` | `str` | `Unspecified` | 5/5 |
| `fetuses[].placenta.thickness` | `int` | `0` | 5/5 |
| `fetuses[].placenta.thickness_user_spec` | `int` | `0` | 5/5 |
| `fetuses[].uards` | `dict` | - | 5/5 |
| `fetuses[].uards.uards` | `dict` | - | 5/5 |
| `fetuses[].uards.uards.a_priori_risk` | `int` | `0` | 5/5 |
| `fetuses[].uards.uards.a_priori_risk_lookup` | `str` | `Unspecified` | 5/5 |
| `fetuses[].uards.uards.maternal_age_risk` | `int` | `22\|29\|37\|47\|61` | 5/5 |
| `fetuses[].uards.uards.risk_adjustment` | `int` | `0` | 5/5 |
| `fetuses[].uards.uards.risk_adjustment_lookup` | `str` | `Unspecified` | 5/5 |
| `fetuses[].uards.uards.ultrasound_adjusted_risk` | `int` | `0` | 5/5 |
| `fetuses[].uards.uards_markers` | `list` | - | 5/5 |

#### EVMS GE HL7

| viewpoint_path | type | sample | files |
| --- | --- | --- | --- |
| `OBX Fetus.PlacentaSite` | `str (ST)` | `anterior` | 2/7 |
| `OBX Fetus.VP_PlacentaDetails_Mask` | `str (ST)` | `left lateral\.br\\.br\\|anterior\.br\\.br\\|posterior, fundal\.br\\.br\\|posterior\.br\\.br\` | 5/7 |
| `OBX UmbilicalCordFetus.CordVessels` | `str (ST)` | `3 vessel cord` | 3/7 |
| `OBX UmbilicalCordFetus.UmbilicalArteryUndefinedEDV` | `str (NM)` | `19.5` | 1/7 |
| `OBX UmbilicalCordFetus.UmbilicalArteryUndefinedHR` | `str (NM)` | `201` | 1/7 |
| `OBX UmbilicalCordFetus.UmbilicalArteryUndefinedMD` | `str (NM)` | `19.21` | 1/7 |
| `OBX UmbilicalCordFetus.UmbilicalArteryUndefinedPI` | `str (NM)` | `0.86` | 1/7 |
| `OBX UmbilicalCordFetus.UmbilicalArteryUndefinedPSV` | `str (NM)` | `42.72` | 1/7 |
| `OBX UmbilicalCordFetus.UmbilicalArteryUndefinedRI` | `str (NM)` | `0.54` | 1/7 |
| `OBX UmbilicalCordFetus.UmbilicalArteryUndefinedSoverD` | `str (NM)` | `2.19` | 1/7 |
| `OBX UmbilicalCordFetus.UmbilicalArteryUndefinedTAmax` | `str (NM)` | `27.08` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPI_Author` | `str (ST)` | `Baschat` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPI_DevRatio` | `str (NM)` | `-20.9` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPI_Deviation` | `str (NM)` | `-1.4` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPI_Percentile` | `str (NM)` | `9` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPSV_Author` | `str (ST)` | `Ebbing` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPSV_DevRatio` | `str (NM)` | `-1.8` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPSV_Deviation` | `str (NM)` | `-0.1` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedPSV_Percentile` | `str (NM)` | `45` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedRI_Author` | `str (ST)` | `Schaffer` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedRI_DevRatio` | `str (NM)` | `-21.3` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedRI_Deviation` | `str (NM)` | `-1.8` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedRI_Percentile` | `str (NM)` | `4` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedSoverD_Author` | `str (ST)` | `Acharya` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedSoverD_DevRatio` | `str (NM)` | `-27.1` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedSoverD_Deviation` | `str (NM)` | `-1.5` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedSoverD_Percentile` | `str (NM)` | `7` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedTAmax_Author` | `str (ST)` | `Ebbing` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedTAmax_DevRatio` | `str (NM)` | `-4.1` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedTAmax_Deviation` | `str (NM)` | `-0.3` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalArteryUndefinedTAmax_Percentile` | `str (NM)` | `39` | 1/7 |
| `OBX UmbilicalCordFetus.VP_UmbilicalCordDetails_Mask` | `str (ST)` | `3 vessel cord\.br\\.br\\|2 vessel cord\.br\\.br\` | 6/7 |

