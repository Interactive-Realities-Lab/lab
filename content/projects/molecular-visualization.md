---
title: "DockPrism: Immersive Inspection of Molecular Docking Evidence in Virtual Reality"
type: page
layout: compact
weight: 70
status: active
featured: false
umbrella: scientific-visualization
umbrella_label: Scientific Visualization
summary: Inspecting molecular docking predictions in virtual reality, with a focus on protein–glycan interactions.
project_image: media/projects/molecular-visualization/docking-setup.png
image_alt: Molecular structure and docking setup controls in DockPrism.
show_project_hero: false
related_people:
- fahmida-imrose
- regis-kopper
---

**Members:** [Fahmida Imrose]({{< relref "/authors/fahmida-imrose" >}}) · [Regis Kopper]({{< relref "/authors/regis-kopper" >}})

Molecular docking predicts how a molecule may bind to a protein, but a favorable score alone does not establish whether a predicted arrangement is physically plausible or biologically meaningful. Researchers also need to examine molecular geometry and contacts to decide which candidates warrant further investigation.

DockPrism explores an integrated virtual reality workflow for molecular docking, with a focus on protein–glycan interactions. It combines docking setup, pose generation with AutoDock Vina, and inspection of candidate poses. By bringing together docking scores, glycan conformations, and protein–glycan contacts, the project aims to help researchers examine cases where these forms of evidence disagree.

Users can compare candidate poses and inspect relevant molecular regions at an enlarged scale while retaining their surrounding structural context. A planned user study will evaluate how this approach supports the interpretation of docking evidence.

{{< project_figure src="media/projects/molecular-visualization/docking-setup.png" alt="A molecular structure beside docking setup controls and a three-dimensional docking region in DockPrism." max_width="640" hover="true" >}}
**Figure 1.** Molecular docking setup in virtual reality.
{{< /project_figure >}}

{{< project_figure src="media/projects/molecular-visualization/pose-inspection.png" alt="Pose inspection panel listing molecular contacts, with a magnified molecular view and surrounding protein structure in DockPrism." max_width="640" hover="true" >}}
**Figure 2.** Inspection of a candidate pose using molecular contacts and a magnified view.
{{< /project_figure >}}
