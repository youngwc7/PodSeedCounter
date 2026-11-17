# Seed counter: user manual

Version 2.5.0. Installation is described in `SETUP.md`.

The seed counter finds the pods in transmitted-light microscope images (`.tif`), counts the seeds in each pod,
draws a border around every seed and tells you which counts it is unsure about. In the **review page** you
check those counts, correct mistakes, confirm images, add new images and annotations, and let the program learn
from your corrections.

Keys in this manual are the default shortcuts; they can be changed (section 16).

## Contents

1. [Starting and stopping](#1-starting-and-stopping)
2. [The screen at a glance](#2-the-screen-at-a-glance)
3. [Moving around the image](#3-moving-around-the-image)
4. [What the colours and lines mean](#4-what-the-colours-and-lines-mean)
5. [Selecting things](#5-selecting-things)
6. [Reviewing seeds: the basic workflow](#6-reviewing-seeds-the-basic-workflow)
7. [Correcting seeds: split, redraw, add, delete](#7-correcting-seeds-split-redraw-add-delete)
8. [Dark areas without a seed](#8-dark-areas-without-a-seed)
9. [Correcting pods](#9-correcting-pods)
10. [Finishing an image, undo and discard](#10-finishing-an-image-undo-and-discard)
11. [The threshold sliders](#11-the-threshold-sliders)
12. [Adding images](#12-adding-images)
13. [Adding annotated images (ground truth)](#13-adding-annotated-images-ground-truth)
14. [The overview](#14-the-overview)
15. [Learning from your reviews](#15-learning-from-your-reviews)
16. [Keyboard shortcuts and how to change them](#16-keyboard-shortcuts-and-how-to-change-them)
17. [Saving results and continuing later](#17-saving-results-and-continuing-later)
18. [The output files](#18-the-output-files)
19. [Working without the review page](#19-working-without-the-review-page)
20. [Changing settings](#20-changing-settings)
21. [Adding ground truth by hand](#21-adding-ground-truth-by-hand)
22. [How the counting works](#22-how-the-counting-works)
23. [Accuracy, limitations and troubleshooting](#23-accuracy-limitations-and-troubleshooting)

---

## 1. Starting and stopping

From the `seed_project` folder:

```
.venv\Scripts\python scripts\review.py
```

(Linux: `.venv/bin/python scripts/review.py`; double-click alternatives are in `SETUP.md`.)

- The first start analyses every image in `input_images\` (about a second per image). Later starts reuse those
  results, so they are almost instant; only new or changed images are analysed.
- With no images yet (as after installation: `input_images\` starts empty), the page opens with an empty list and
  an *Add images* button (section 12).
- The browser then opens **http://localhost:8000**. If it does not, type that address yourself.
- **Stop** with **Ctrl+C** in the terminal window. Everything you did is already saved (section 17).
- Only your own computer can open the page. Closing the browser tab does not stop the program; just open the
  address again.

Useful start options (all optional):

| Option | Effect |
|---|---|
| `D:\scans\batch3` | Use another folder of images instead of `input_images\` |
| `-o D:\scans\batch3_results` | Use another output folder (your review work is kept there too) |
| `--port 8001` | Use another port, e.g. if 8000 is taken; the address becomes http://localhost:8001 |
| `--no-browser` | Do not open the browser automatically |
| `-c my_settings.yaml` | Use another settings file |
| `--keys my_keys.yaml` | Use another shortcut file |
| `--gt D:\annotations` | Use another ground-truth folder |
| `--host 0.0.0.0` | Let other computers on your network open the page (there is no login; ask IT first) |

Example: `.venv\Scripts\python scripts\review.py D:\scans\batch3 -o D:\scans\batch3_results --port 8001`

## 2. The screen at a glance

```
+------------------------------------------------------------------------------------------------+
| Seed review | Review threshold ---o--- | Reject threshold --o---- | Add images | Add annotation  |
|             |                          |                          | Overview | Learn from reviews |
|             |                          |                          | Undo | Save results            |
+-------------+------------------------------------------------------+---------------------------+
| Image list  | Toolbar: Select | Add seed | Split seed | Redraw      | Image: name, status,      |
|             |          border | Fit | layer switches                |   counts, buttons         |
| image 1  ok |                                                      | Selection card            |
| image 2  !! |               the image with seed borders            | Next to check             |
| ...         |                                                      | Pods table                |
|             | zoom %                                               | Keys                      |
+-------------+------------------------------------------------------+---------------------------+
```

**Top bar**

| Element | What it does |
|---|---|
| Review threshold, Reject threshold | Sliders that decide the seed colours and pod review flags (section 11) |
| Add images | Add TIFF files to the input folder (section 12) |
| Add annotation | Add a raw image with its annotated copy as ground truth (section 13) |
| Overview | All images in one table, with progress (section 14) |
| Learn from reviews | Tune the program on the images you checked (section 15) |
| Undo | Undo your last change to the current image |
| Save results | Write the report, tables and annotated images with your corrections (section 17) |

**Image list (left)**: every image, with its review status as a coloured chip and a coloured left edge
(green *no*, orange *maybe*, red *yes* or *error*), a ✓ when you have marked it as checked, and a line like
*147 seeds, 6 pods, 3 to check, 2 edits*. Click an image to open it.

**Image area (centre)**: the image with all pods and seed borders. The toolbar at the top left switches drawing
modes and layers; the zoom level is shown at the bottom left.

**Details panel (right)**, from top to bottom:

- **Image**: file name, status chip, total seeds and pods, a green/orange/red bar with the seed counts per
  colour, the automatic count (and the change you made), notes about the image.
- **Mark image as checked** and **Discard edits** (section 10).
- **Selection**: details and buttons for whatever you clicked (a seed, a dark area or a pod).
- **Next to check**: jumps to the next item that needs your attention, with the number left. Below it, the
  option *Go to the next one after each decision*.
- **Pods**: one row per pod: seed count, automatic count with change, colour bar, pod confidence, review flag,
  and underneath the reason for the flag and your edits. Click a row to zoom to that pod and select it.
- **Keys**: the current keyboard shortcuts.

## 3. Moving around the image

| To | Do |
|---|---|
| Zoom in and out | Mouse wheel; zooms towards the mouse pointer (2 % to 1200 %) |
| Move the image | Drag with the left mouse button (in Select mode) |
| Move the image in a drawing mode | Drag with the right mouse button, or hold Shift while dragging |
| See the whole image | **F**, or the *Fit* button |
| Go to a pod | Click its row in the Pods table |
| Go to the next item to check | **N** (previous: **Shift+N**) |
| Previous / next image | **[** / **]** |

**Layer switches** in the toolbar hide or show parts of the drawing, which helps to see the seeds underneath:

| Switch | Shows |
|---|---|
| Seeds | All seed borders |
| Centerline and cuts | The red centerline and the blue bud and stem cuts |
| Dark areas | The magenta dashed areas (section 8) |
| Rejected | Rejected seeds (dashed grey) |

## 4. What the colours and lines mean

**Seed borders**

| Look | Meaning |
|---|---|
| Green | Confident. Also every seed you accepted, redrew or added. |
| Orange | The program is unsure: worth a look |
| Red | Likely wrong: e.g. two seeds in one border, or a dark patch that is not a seed |
| Grey, dashed | Not counted: rejected by you, or outside the bud and stem cuts |
| Blue with a white halo | The selected item |
| White, dashed (selected seed only) | The original automatic border of a seed you redrew |

All green, orange and red seeds are counted; the colour only says how much to trust each border. Which
confidence counts as green, orange or red is set with the sliders (section 11).

**Other lines and marks**

| Look | Meaning |
|---|---|
| Thin dark outline | A pod |
| Grey dashed pod outline | A pod you marked as *not a pod*; it is not counted |
| Red line along the pod | The pod centerline: seeds lie in a top and a bottom row on either side of it |
| Thin blue line at the left end | The bud cut: nothing left of it is counted (the round bud is never a seed) |
| Thick blue line at the right end | The stem cut: nothing right of it is counted (where the pod meets the stem) |
| Magenta dashed outline | A dark, seed-sized area that no seed border covers: possibly a missed seed (section 8) |
| Number left of a pod | The pod's seed count, coloured by its review flag (green *no*, orange *maybe*, red *yes*) |

**Review flags** (*needs review*): each pod gets a *pod confidence* between 0 and 1: an estimate of how likely
its count is right. It goes down for uncertain seeds, unexplained dark areas, and a bud or stem end outside the
image. The flag follows from the same two sliders:

| Pod confidence | Needs review |
|---|---|
| at or above the review threshold | **no** |
| between the two thresholds | **maybe** |
| below the reject threshold | **yes** |

An image takes the flag of its worst pod. An image you marked as checked is always *no*.

## 5. Selecting things

In **Select** mode (**S**, or the *Select* button), click:

| Click on | Selects | The Selection card shows |
|---|---|---|
| A seed | That seed (if borders overlap, the smallest) | Status, confidence, row, area, buttons |
| A magenta dashed area | That dark area | Size, status, buttons |
| An empty part of a pod | The pod | Counts, confidence, pod buttons |

**Esc** clears the selection. The seed card shows:

| Field | Meaning |
|---|---|
| Status | *automatic*, *accepted by you*, *added by you*, *part of split seed …*, *rejected (not counted)*, *outside the cuts (not counted)*; with *, border redrawn* when you redrew it |
| Confidence | The program's confidence (0 to 1) that this is a real, separately counted seed |
| Row | Top or bottom row (relative to the centerline) |
| Area | Size in pixels, and how it compares with a typical seed (e.g. *2.28 x typical* suggests two seeds) |
| Across line | How much of the seed lies on the other side of the centerline (high values suggest two seeds) |
| Note | *split from a merged object* when the program itself separated it from a neighbour |

## 6. Reviewing seeds: the basic workflow

1. Open an image that needs review (orange or red in the image list).
2. Press **N** (or click *Next to check*). The view zooms to the first orange or red seed, or open dark area,
   working through the pods from top to bottom and each pod from left to right.
3. Decide:
   - **A**, *Accept*: it is one real seed and the program found it correctly. It turns green.
   - **R**, *Reject*: it is not a seed. It is no longer counted and stays visible as a dashed grey outline.
   - It is two seeds in one border: split it (section 7).
   - The seed is right but its border is wrong: redraw it (section 7).
4. With *Go to the next one after each decision* ticked, the next item opens automatically; otherwise press **N**.
5. When *Next to check* says *Nothing left to check*, look over the image once more (missed seeds, pod ends),
   then press **C** to mark it as checked (section 10).

Changed your mind? Select the item and press **U** (*Undo decision*): it returns to the program's original
state. **Ctrl+Z** undoes your last change of any kind.

Accepting means *"this seed was detected correctly"*. It does **not** approve the shape of its border; only
redrawing does (this matters for learning, section 15).

## 7. Correcting seeds: split, redraw, add, delete

### Split a seed (two seeds in one border): **X**

1. Press **X** (or *Split seed* in the toolbar, or *Split* in the seed card).
2. Drag a straight line through the seed where its two parts meet. The line may start and end outside the seed.
3. The border is replaced by two seeds (both green, *part of split seed …*). The count goes up by one.

The line is applied to the seed it crosses most. Both parts must be reasonably large; otherwise you get a message
and nothing changes. The tool stays active so you can split more seeds; press **Esc** to return to Select mode.
To undo a split, select either part and press **U** (or click *Undo split*).

### Redraw a border (the seed is right, its border is not): **D**

1. Select the seed (click it, or reach it with **N**).
2. Press **D** (or *Redraw border* in the toolbar, or *Redraw* in the seed card).
3. Trace the correct outline with the mouse in one stroke. Releasing the mouse closes the shape.

The seed keeps its number and stays counted, and turns green. While it is selected, its original automatic border
is shown as a white dashed line. Redraw again if needed (the original is still kept); **U** brings the original
border back. Only redrawn borders teach the program what seeds look like (section 15).

### Add a missed seed: **E**

1. Press **E** (or *Add seed*).
2. Drag over the seed: an upright ellipse is drawn from corner to corner of your drag. It must lie inside a pod.
3. The new seed is green and *added by you*; the count goes up by one.

The tool stays active for adding more seeds; **Esc** returns to Select mode. For an irregular shape, add the
seed with an ellipse and then redraw its border (**D**).

### Delete a seed you added: **Delete** (or Backspace)

Select it and press **Delete**, or click *Delete*. Seeds the program found cannot be deleted; reject them
instead (**R**), so the record of what the program did is kept.

## 8. Dark areas without a seed

A **magenta dashed outline** marks a dark, seed-sized area that no seed border covers. It may be a seed the
program missed, or just shadow, tissue or debris. Open dark areas count against the pod's confidence and appear
in *Next to check*.

Select it (click it, or reach it with **N**), then:

| Key / button | Effect |
|---|---|
| **A**, *Add as seed* | A seed is created from the area's outline (redraw it with **D** if the outline is poor) |
| **R**, *Not a seed* | The area is dismissed: hidden, and no longer counts against the pod |
| **U**, *Undo* | Brings a dismissed area back |

You can also draw the seed yourself with *Add seed*; an area covered by a seed no longer counts as open.

## 9. Correcting pods

Click an **empty part of a pod** (or its row in the Pods table) to select the pod. The Selection card then offers:

### Move bud cut / Move stem cut

Click *Move bud cut* (or *Move stem cut*), then click inside the pod where the cut belongs. Seeds left of the bud
cut or right of the stem cut are not counted; they stay visible as dashed grey. Use this when the program put a
cut in the wrong place (for example counted the bud, or cut off the last seed). If you extend the pod, add any
seeds in the new part with *Add seed*.

### Split pod

For two touching pods that were detected as one: click *Split pod*, then drag a line through the pod along the
gap between the two pods. Each part becomes a pod with its own seeds and cuts (check the cuts afterwards). The new
pod gets the next free pod number.

### Merge with

For one pod detected as two pieces: choose the other piece in *Merge with* and click *Merge*. The seeds of both are
combined into the selected pod.

### Not a pod / Count this pod again

*Not a pod* is for something that is not a pod at all (debris, a loose stem). It is drawn with a grey dashed
outline, has no number and is not counted. Select it and click *Count this pod again* to undo.

## 10. Finishing an image, undo and discard

| Button / key | Effect |
|---|---|
| **C**, *Mark image as checked* | You confirm the whole image. It gets a ✓, its status becomes *no*, its pods show *checked by reviewer*, and it can be used for learning (section 15). Press again (*Mark as not checked*) to undo. |
| **Ctrl+Z**, *Undo* | Undoes your last change to this image; repeat to go further back. Each image has its own history, which survives restarts. |
| **U** | Undoes the decision on the selected item only (accept, reject, redraw, split, dismiss) |
| *Discard edits* | Removes **all** your changes to this image and analyses it again with the current settings (you are asked to confirm) |

## 11. The threshold sliders

The two sliders at the top decide the colours and flags; they do not change the counts.

| Slider | Meaning |
|---|---|
| Review threshold (default 0.70) | Seeds with at least this confidence are **green**; pods with at least this confidence need **no** review |
| Reject threshold (default 0.40) | Seeds below this are **red**; pods below this need review (**yes**). In between: orange / *maybe* |

- Moving a slider recolours everything at once, for all images, without analysing again.
- The reject threshold can never be above the review threshold; the sliders push each other if needed.
- Raising the review threshold makes the program more cautious: more orange seeds and more pods to check.
- The slider positions are used by *Save results* and written into the report, but they are not stored in the
  settings: reloading the page brings back the values from `config\default.yaml`. To change the defaults, edit
  `confidence.review_threshold` and `confidence.reject_threshold` there (section 20).
- Seeds you accepted, redrew or added stay green at any slider position.

## 12. Adding images

1. Click **Add images**.
2. Drop `.tif` / `.tiff` files onto the dashed area, or click it to choose files (several at once is fine).
3. Each file is uploaded and checked, then all new images are analysed (a progress bar shows how far).
4. They appear at the end of the image list, ready to review. No restart is needed.

| Situation | What happens |
|---|---|
| The same file is already in the input folder | Skipped (*already in the input folder*) |
| A different file with the same name exists | Refused, so nothing is overwritten. Rename your file and add it again. |
| The file is not a readable TIFF | Refused, with the reason |

The files are copied into the input folder (`input_images\` unless you started the review with another folder),
so they are also there for the next start and for `run_count.py`.

## 13. Adding annotated images (ground truth)

Annotated images are images in which a person has outlined every seed. The program uses them to check itself and
to learn (section 15).

### Preparing an annotation

- Use a copy of the **full, uncropped** image. Any size is fine (it is scaled back), but the proportions must be
  the same as the TIFF.
- Draw a **closed white outline** around each seed. Gaps in a line make the shape "open", and an open shape is
  not counted.
- Numbers, other lines and the blue stem bar may stay on the image; they are ignored. Handwritten counts on the
  image are **not** read: you type the counts in the dialog.
- Save as PNG if you can. JPEG works, but blurs thin lines.

### Adding it

1. Click **Add annotation**.
2. Choose the **raw image** (the original `.tif`) and the **annotated image**, then click **Check**.
3. The dialog shows a preview: the raw image with the recognised outlines in **magenta** and each pod numbered.
   Click the preview to open it larger in a new tab.
4. The table lists every pod with the number of enclosed **shapes** found. Type the **seed count** of each pod
   (from your annotation, top to bottom as numbered in the preview).
5. Each row shows whether shapes and count agree:

| Shown | Meaning | Usual cause |
|---|---|---|
| ✓ match | The number of outlined shapes equals your count | |
| *2 fewer* | Fewer shapes than your count | An outline is not closed, or a seed has no outline |
| *2 more* | More shapes than your count | A gap enclosed between touching outlines was taken as a shape |

   The total number of shapes, and any shapes outside all pods, are shown above the table.
6. Fix the annotation and check again, or click **Save annotation**. If some pods differ you are asked to confirm;
   your typed counts are then the truth, and the outlines are still used to match individual seeds.

Saving copies the raw image to `ground_truth\raw\` and the annotation to `ground_truth\annotations\` (renamed
to `<image name>_annotation.<ext>`), and adds an entry to `ground_truth\manifest.yaml`.

### Existing annotations

The bottom of the dialog lists the annotations in the ground-truth folder. **Remove** takes one out of the
manifest and moves its files to `ground_truth\removed\` (nothing is deleted). An image that is already annotated
must be removed before it can be added again.

If the two files have different proportions, the check stops with a message: annotate the full, uncropped frame.

## 14. The overview

Press **O** or click **Overview** to replace the image with a table of all images. Press **O** or *Back to image*
to return.

- The heading shows progress (*12 of 40 images checked; 5 still need review*) with a progress bar.
- Once images are checked, a line shows how much your reviews changed the automatic counts on them
  (e.g. *by 14 seeds in total, 1.2 %*): a running measure of the program's accuracy.
- **Show** filters the table: all images, not checked, needing review, with red seeds, edited.
- Click a column heading to sort by it (click again to reverse). Click a row to open that image.

| Column | Meaning |
|---|---|
| Image, Needs review, Checked | Name, status, ✓ when checked |
| Seeds | The current count, with your corrections |
| Automatic | The count the program found |
| Change | Seeds - Automatic |
| Orange / red | Seeds still orange or red |
| Flagged pods | Pods with *maybe* or *yes* |
| Redrawn | Seeds whose border you redrew |
| Edits | Number of changes you made |

## 15. Learning from your reviews

Every image you **mark as checked** becomes ground truth. Your corrections teach the program:

| Your action | Teaches which seeds are right (detection and counts) | Teaches seed shape (borders) |
|---|---|---|
| Accept (**A**) | yes | no |
| Reject, add, split, dark areas, pod corrections | yes | no |
| Redraw (**D**) | yes | **yes** |

Accepting confirms detection only, so odd automatic borders never teach the program their shape. Only borders
you explicitly redrew do. Seeds you did not touch on a checked image count as correct.

**Running it**

1. Check several images of each kind you work with (e.g. dense and pale pods). Redraw wrong borders on them if you
   want the borders to improve.
2. Click **Learn from reviews**.
3. Choose:
   - *Also use the annotated images in ground_truth/*: include your annotations (section 13). If an image is both
     annotated and checked, the checked version is used.
   - *Also tune the detection settings*: tries many combinations of the detection settings (a few minutes for a
     handful of images; longer for many). Untick it to only re-fit the confidence colours (seconds).
4. Click **Start**. When it is done, the dialog compares the current and the new settings:
   - **Count error over all pods**: the total difference between counted and true seeds per pod (lower is better),
     and the *seed F1* (how well individual seeds are found, 1 = perfect).
   - **Border overlap**: how well detected borders overlap your redrawn ones (1 = identical). Shown only when you
     have redrawn borders; without them, border shape plays no part.
5. Click **Use the new settings** to keep them. They are written into `config\default.yaml` (the old file is kept
   as `config\default.backup.yaml`) and every image you have **not** edited is analysed again. Images you edited
   keep the analysis you reviewed.

**Cautions**

- The scores are measured on the same images the settings were tuned on, so they look better than they will be
  on new images. A handful of checked images can over-fit; a few dozen of each kind is a much better basis.
- Learning tunes seed detection and confidence. It does not change how pods are found, so pod corrections fix the
  image you are on but do not teach pod detection.
- The same is available without the page: `calibrate.py --from-reviews` (section 19).

## 16. Keyboard shortcuts and how to change them

| Default key | Action |
|---|---|
| **A** | Accept the seed / add the dark area as a seed |
| **R** | Reject the seed / mark the dark area as not a seed |
| **U** | Undo the decision on the selected item (also undoes a redraw or split) |
| **Delete**, Backspace | Delete a seed you added |
| **N** / **Shift+N** | Next / previous item to check |
| **[** / **]** | Previous / next image |
| **O** | Show or hide the overview |
| **S** | Select mode |
| **E** | Add seed mode |
| **X** | Split seed mode |
| **D** | Redraw border of the selected seed |
| **Esc** | Leave a drawing mode; in Select mode, clear the selection |
| **F** | Fit the whole image |
| **C** | Mark the image as checked / not checked |
| **Ctrl+Z** | Undo the last change to this image |
| Mouse wheel | Zoom |
| Drag | Move the image (in drawing modes: right-drag or Shift-drag) |

Shortcuts do nothing while you type in a box or while a dialog is open.

### Changing shortcuts

The shortcuts are in **`config\keybindings.yaml`**. Each line is an action with a list of keys:

```yaml
accept: [A]
reject: [R]
delete: [Delete, Backspace]
undo: [Ctrl+Z]
```

1. Open the file in a text editor (Notepad is fine) and change the keys, e.g. `accept: [Space]`.
2. Save it and **reload the page** in the browser (F5). No restart is needed.

Rules:

- Letters and digits: `A`, `7` (case does not matter). With modifiers: `Shift+N`, `Ctrl+Z`, `Alt+A`,
  `Ctrl+Shift+Z` (Ctrl also matches Cmd on a Mac).
- Other characters in quotes: `"["`, `"?"`. Write the character itself, not `Shift+` and a key.
- Named keys: `Delete`, `Backspace`, `Escape`, `Enter`, `Space`, `Tab`, `Home`, `End`, `PageUp`, `PageDown`,
  `ArrowLeft`, `ArrowRight`, `ArrowUp`, `ArrowDown`, `F1` to `F12`.
- Several keys per action: `delete: [Delete, Backspace]`. No shortcut: `overview: []`.
- A key can belong to one action only. Actions you leave out keep their default key; if you give an action's
  default key to another action, the first action has no key until you give it one.
- Avoid keys the browser uses itself (Ctrl+W, Ctrl+R, F5).

Problems in the file (unknown action, invalid key, a key used twice) are shown as a red message when the page
loads; the rest of the file still works. The *Keys* list in the panel and the key hints on buttons always show
the shortcuts actually in effect.

## 17. Saving results and continuing later

**Your work is saved automatically** after every change, in `output\review\sessions\` (one file per edited image,
holding the analysis you reviewed and the list of your changes). You can close the browser or stop the program at
any time; start it again to continue exactly where you were, including the undo history.

**Save results** writes the normal output files (section 18) into the output folder, with all corrections and the
current slider positions:

- annotated images with the corrected borders and counts,
- the tables with corrected counts, the automatic counts and changes, a *reviewed* column, and the edits per pod
  in the *reason* column (e.g. *edits: 2 added, 1 rejected, 1 redrawn*),
- the report, which also states how much review changed the counts on checked images.

It overwrites the previous output files (not your review work). Save again whenever you want an up-to-date set.

**When settings change** (after *Use the new settings*, or editing `config\default.yaml`): images you have not
edited are analysed again with the new settings. Images you edited keep the analysis you worked on; the page notes
this, and *Discard edits* re-analyses such an image (losing its edits).

Where things are kept:

| Location | Contents |
|---|---|
| `output\review\sessions\` | Your edits, one file per image (keep this folder when updating the program) |
| `output\review\cache\` | Stored automatic analyses (can be deleted; they are recreated) |
| `output\review\staging\` | Annotation uploads in progress (can be deleted) |

## 18. The output files

| File | Contents |
|---|---|
| `output\report.html` | The report: open in any browser. Summary of all images, then per image a thumbnail (click for the full image) and the pod table; click *+ Pod n* to see every seed. A checkbox shows only images needing review. |
| `output\annotated_images\<image>_annotated.png` | Each image with seed borders coloured by confidence, the count next to each pod, centerline, cuts and dark areas, and a header with the totals and review status |
| `output\output_table\run_summary.csv` | One row per image, plus a TOTAL row |
| `output\output_table\pods.csv` | One row per pod |
| `output\output_table\report_outline.csv` | Everything in one sheet: a RUN row, IMAGE rows and indented pod rows |
| `output\results.json` | Run settings and summary; with `output.results_json: full`, every pod and seed |
| `output\output_table\seeds.csv` | One row per seed (only with `output.seeds_csv: true`) |

**Columns of `run_summary.csv`**: image, pods, seeds, auto_seeds (automatic count), change, green, orange, red,
pods_no, pods_maybe, pods_yes, needs_review, reviewed, note, annotated_image.

**Columns of `pods.csv`**: image, pod, seed_count, auto_count, change, top_row, bottom_row, green, orange, red,
pod_confidence, needs_review, reviewed, reason.

**Columns of `report_outline.csv`**: level (RUN / IMAGE / pod), image, pod, seeds, auto_count, change, top_row,
bottom_row, green, orange, red, confidence, needs_review, reviewed, reason.

**Google Sheets**: *File → Import → Upload*, choose a CSV, then *Insert new sheet(s)*. Import the CSVs one by one to
get one tab each. In `pods.csv`, *Data → Create a filter* (or a pivot table with rows *image* → *pod*) gives the
image/pod hierarchy.

## 19. Working without the review page

All commands are run from the `seed_project` folder with the `.venv` Python (`python` below means
`.venv\Scripts\python`).

**Count a folder of images and write all outputs** (no review):

```
python scripts\run_count.py
python scripts\run_count.py D:\scans\batch3 -o D:\scans\batch3_results
python scripts\run_count.py --review-threshold 0.8 --reject-threshold 0.5
python scripts\run_count.py --set output.seeds_csv=true --set output.results_json=full
```

**Check the program against the ground truth**:

```
python scripts\evaluate.py              per-pod counts vs. hand counts, seed recall and precision
python scripts\evaluate.py --check-gt   check annotations: outline counts vs. hand counts, with preview images
```

**Tune the settings** (the same as *Learn from reviews*):

```
python scripts\calibrate.py                         tune on ground_truth\ -> config\calibrated.yaml + report
python scripts\calibrate.py --apply                 ... and write the result into config\default.yaml (backup kept)
python scripts\calibrate.py --from-reviews --apply  also use the images checked in the review
python scripts\calibrate.py --reviews-only          only the checked images
python scripts\calibrate.py --no-sweep              only re-fit the confidence colours (fast)
```

The calibration report is written to `output\calibration\report.md`, with every tested setting in `sweep.csv`.
Every script explains its options with `--help`.

## 20. Changing settings

All settings, each with an explanation, are in `config\default.yaml`. Ways to change them:

1. Edit `config\default.yaml` in a text editor.
2. Make a file with only the settings you change and use it with `-c my_settings.yaml` (review and scripts).
3. Override for one run of a script: `--set section.key=value` (repeatable).

Most useful settings:

| Setting | Meaning |
|---|---|
| `confidence.review_threshold`, `confidence.reject_threshold` | Default positions of the two sliders |
| `processing.seed_radius_px` | Expected seed radius in pixels (26 at the examples' magnification). Re-estimated automatically when an image's seeds are clearly larger or smaller. |
| `output.*` | Which files to write; `results_json`: `run` (settings and summary), `full` (every pod and seed) or `off` |
| `segmentation.*`, `contrast.*` | Seed detection; best changed through learning or calibration |
| `calibration.sweep` | Which settings learning tries, and which values |
| `calibration.border_weight` | How much border overlap counts when learning (only with redrawn borders) |
| `calibration.border_sources` | `[redrawn]` (default). Add `annotations` to also let hand-drawn outlines in `ground_truth\` teach border shape. |
| `render.*` | Size and line width of the annotated images and thumbnails |

## 21. Adding ground truth by hand

The easiest way is *Add annotation* (section 13). Without the page:

1. Copy the raw TIFF into `ground_truth\raw\`.
2. Put the annotated copy (section 13, *Preparing an annotation*) into `ground_truth\annotations\`.
3. Fill in the empty entry in `ground_truth\manifest.yaml` (or add a new one below it for each further image),
   with your counts per pod from top to bottom:

   ```yaml
   - image: my_new_image.tif
     annotation: my_new_image_annotated.png
     pod_counts: [31, 28, 30, 25]
   ```

   `pod_counts` is optional (the outlines are counted instead) but recommended. An entry whose fields are all empty
   is ignored. An annotation with the same file name as the TIFF (e.g. `my_new_image.png`) is found even without an
   entry.
4. Check it: `python scripts\evaluate.py --check-gt`.

A broken entry (missing file, wrong proportions, malformed counts) produces a note and is skipped; the others are
still used.

## 22. How the counting works

1. **Loading**: the largest page of the TIFF (multi-page, compressed and 16-bit files are handled), analysed at half size.
2. **Pods**: separated from the white background by colour saturation and numbered from top to bottom. Pods may
   touch or overlap: where a column of the pod area is much taller than one pod (1.4 pod widths), two pods are
   fused there. They are cut apart along a smooth seam through the palest pixels; where the two pods part next to
   the fused stretch, the seam is joined to that real gap, otherwise it is followed until they part. Such pods are
   noted "pod touched another pod; separated automatically along the seam". The top and
   bottom outline of each pod is traced; the **centerline** is their smoothed middle. The **bud cut** is where the pod
   reaches 60 % of its width (and at least half a pod width from the tip); the **stem cut** is where the width drops
   below 60 % at the stem.
3. **Contrast**: seeds absorb green light most, so a seed shows up as an area of the green channel that is darker
   than the surrounding pod. Comparing with the local pod tone makes this work for dark and pale pods alike.
4. **Seeds** (elliptical shape filter): the contrast map is compared with seed-shaped ellipses of several sizes,
   lengths and angles (dark inside, lighter ring around). Seeds lie lengthwise in the pod, so the long axis may turn
   at most 30 degrees from the pod axis. Every local best match is a candidate seed with its own ellipse; candidates
   are accepted strongest first. A candidate is rejected if its ellipse is not filled by one dark spot (e.g. it sits
   on the gap between two seeds), if it is much paler than the pod's typical seed, or if its core is already taken by
   an accepted seed. Touching and slightly overlapping seeds are therefore separated by their shape, not by a
   minimum distance or by darkness alone. A seed's border is its ellipse. The earlier darkest-point method is still
   available with `segmentation.method: contrast`.
5. **Confidence**: each seed's confidence comes from its contrast, size, shape, how far it crosses the centerline,
   whether it shares one dark area with another seed (it was separated from a touching seed), and how close it is to a pod end. The pod confidence combines its seeds' confidences, open
   dark areas and missing pod ends.

## 23. Accuracy, limitations and troubleshooting

**Accuracy on the two example images** used during development (version 2.4 with the earlier darkest-point
method, after tuning on these same images, so optimistic; version 2.5's elliptical filter has not yet been
re-measured on them: run `python -m pytest` with the example images in `tests/data`, or `scripts/evaluate.py`):

| Image | Program, per pod | Hand count, per pod | Total |
|---|---|---|---|
| d98bd67c-1_Col_0002 | 59, 54, 63, 47, 47 | 58, 54, 62, 48, 46 | 270 vs 268 |
| 09_1829px6_06 | 29, 19, 20, 31, 24, 24 | 27, 19, 20, 32, 23, 24 | 147 vs 145 |

The total per-pod error is 8 seeds over 11 pods (1.9 %); the pod with the largest error is the one flagged *maybe*.

Version 2.5 was developed on `07_1827px6_08` (six pods, two pairs touching; tuned on this image, so optimistic):

| Version | Program, per pod | Hand count, per pod | Total | Per-pod error |
|---|---|---|---|---|
| 2.4 | 4 pods found: 38, 55, 48, 23 | 29, 23, 28, 19, 23, 22 | 164 vs 144 | pods merged |
| 2.4 + pod separation | 38, 24, 32, 22, 29, 23 | 29, 23, 28, 19, 23, 22 | 168 vs 144 | 24 seeds |
| 2.5 | 30, 23, 28, 21, 23, 22 | 29, 23, 28, 19, 23, 22 | 147 vs 144 | 3 seeds (2.1 %) |
Expect larger errors on new kinds of images until some of them are checked and the program has learned from them.

**Limitations**

- Pods should lie roughly horizontally, bud on the left, stem on the right, on a white background. Strongly tilted
  pods are flagged. Touching pods are separated automatically and flagged; this needs most pods of the image to be
  apart somewhere (their typical width is measured where they are apart). If a seam is wrong, use *Split pod*.
- The elliptical filter assumes seeds lie lengthwise (within 30 degrees of the pod axis); change
  `segmentation.ellipse.max_angle_to_pod` if your seeds lie across the pod.
- Seeds that overlap almost completely may be counted as one; a single elongated seed across the centerline is
  occasionally split in two. Both usually show orange or red.
- Handwritten numbers on annotations are not read.

**Troubleshooting**

| Problem | Solution |
|---|---|
| The browser does not open | Type http://localhost:8000 yourself (or the port you chose) |
| *cannot use port 8000* | The review is probably already running in another window: use that one, or start with `--port 8001` |
| *Cannot reach the review server* in the page | The program was stopped: start it again and reload the page |
| A key does nothing | Click on the image first (a box or dialog may have the focus); check the Keys list for the current shortcuts |
| A red message about the shortcut file | Fix the line it names in `config\keybindings.yaml` and reload the page |
| An image has far too many or too few pods | The background may not be white enough, or the pods very pale: see `pods.saturation_margin` in the settings |
| *Application Control* or *blocked* messages | See `SETUP.md`, section 7 |
| A double-clicked `.bat` file does nothing | See `SETUP.md`, sections 7 and 8, or use the typed command |
