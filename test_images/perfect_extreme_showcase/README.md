# Perfect Extreme Attack Showcase - Hybrid Verification

## How It Works

This showcase demonstrates watermark detection using the same **hybrid verification** system as the website:

1. **Exact Match** - Direct hash lookup
2. **Fuzzy Match** - Character similarity (50%+ match)
3. **Perceptual Hash** - Visual similarity fallback

Even when the watermark is corrupted by extreme attacks, the system can still **identify the image** and display the **clean database record**.

## Results: 13/15 Verified

1. **extreme_jpeg_q10** - Extreme JPEG Compression - Quality 10 (90% compression)
   - Method: PERCEPTUAL_HASH
   - Confidence: 40.0%

2. **extreme_dark_0.4** - Severe Darkening - 60% brightness reduction
   - Method: PERCEPTUAL_HASH
   - Confidence: 40.0%

3. **extreme_bright_1.7** - Severe Brightening - 70% brightness increase
   - Method: PERCEPTUAL_HASH
   - Confidence: 40.0%

4. **extreme_scale_0.5x** - Massive Scaling - 50% reduction then upscale
   - Method: EXACT_MATCH
   - Confidence: 100.0%

5. **extreme_blur_11x11** - Heavy Gaussian Blur - 11x11 kernel
   - Method: FUZZY_MATCH
   - Confidence: 50.0%

6. **extreme_noise_sigma15** - Heavy Gaussian Noise - Sigma=15
   - Method: EXACT_MATCH
   - Confidence: 100.0%

7. **extreme_contrast_0.4** - Extreme Contrast Reduction - 60% reduction
   - Method: PERCEPTUAL_HASH
   - Confidence: 40.0%

8. **extreme_grayscale** - Grayscale Conversion
   - Method: EXACT_MATCH
   - Confidence: 100.0%

9. **extreme_posterize** - Heavy Posterization - 4 color levels
   - Method: PERCEPTUAL_HASH
   - Confidence: 30.0%

10. **extreme_combined_jpeg30_dark0.5** - Combined - JPEG Q30 + 50% darker
   - Method: FUZZY_MATCH
   - Confidence: 91.7%

11. **extreme_combined_jpeg40_noise12** - Combined - JPEG Q40 + Heavy noise
   - Method: PERCEPTUAL_HASH
   - Confidence: 40.0%

12. **extreme_combined_scale0.7_blur5** - Combined - Scale 0.7x + Blur 5x5
   - Method: EXACT_MATCH
   - Confidence: 100.0%

13. **extreme_combined_bright0.6_contrast0.6** - Combined - Brightness + Contrast 0.6x
   - Method: FUZZY_MATCH
   - Confidence: 91.7%

