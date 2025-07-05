# Path to your Python script
$scriptPath = ".\generate_overlay_images.py"

# Directory where images are saved (target overlay folder)
$overlayDir = ".\static\overlays"

# Temporary directory where Python saves images before replacement (adjust if needed)
# Assuming your Python script saves images directly to $overlayDir, this may be skipped.
# If Python saves elsewhere, set $tempDir accordingly:
$tempDir = $overlayDir  # If same folder, no copy needed.

# List of overlay images to be replaced
$images = @(
    "feedback_highlight.png",
    "half_tick.png",
    "cross.png",
    "tick.png",
    "icon_1.png",
    "icon_2.png",
    "icon_3.png",
    "manual_override.png",
    "marked_background.png",
    "crossed_full_tick.png"
)

# Run the Python script to generate new images
Write-Host "Running Python image generation script..."
python $scriptPath

if ($LASTEXITCODE -ne 0) {
    Write-Error "Python script failed. Aborting image replacement."
    exit 1
}

# Remove existing images in the overlay folder
foreach ($img in $images) {
    $imgPath = Join-Path $overlayDir $img
    if (Test-Path $imgPath) {
        Write-Host "Removing existing image: $imgPath"
        Remove-Item $imgPath -Force
    }
}

# If Python saved images to a different temp folder, copy them to $overlayDir here:
# (Skip if $tempDir == $overlayDir)
# foreach ($img in $images) {
#     $srcPath = Join-Path $tempDir $img
#     $destPath = Join-Path $overlayDir $img
#     if (Test-Path $srcPath) {
#         Write-Host "Copying $img to overlay directory."
#         Copy-Item $srcPath -Destination $destPath -Force
#     } else {
#         Write-Warning "Generated image not found: $srcPath"
#     }
# }

Write-Host "All old images removed. New images should now be in place."

# Verify images exist
foreach ($img in $images) {
    $imgPath = Join-Path $overlayDir $img
    if (-Not (Test-Path $imgPath)) {
        Write-Warning "Warning: $img was not created."
    } else {
        Write-Host "Verified image exists: $img"
    }
}
