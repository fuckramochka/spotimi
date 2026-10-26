package mi.spotimi;

import android.graphics.Color;

/**
 * Runtime palette manager for Spoti Mi.
 * 
 * Maps Spotify's stock green family into the Gothic Kawaii Pink aesthetic
 * dynamically in memory for values parsed or constructed at runtime.
 */
public final class Palette {
    public static final int STOCK_GREEN = 0xFF1DB954;
    private static final float HUE_TOLERANCE = 35.0f;
    private static final float MIN_SAT = 0.25f;
    private static final float MIN_VAL = 0.20f;

    private Palette() {}

    /**
     * Checks if a given ARGB colour belongs to the Spotify Green family.
     */
    public static boolean isStockGreen(int color) {
        float[] hsv = new float[3];
        Color.colorToHSV(color, hsv);
        float sat = hsv[1];
        float val = hsv[2];

        if (sat < MIN_SAT || val < MIN_VAL) {
            return false;
        }

        float[] refHsv = new float[3];
        Color.colorToHSV(STOCK_GREEN, refHsv);

        float diff = Math.abs(hsv[0] - refHsv[0]);
        if (diff > 180.0f) {
            diff = 360.0f - diff;
        }
        return diff <= HUE_TOLERANCE;
    }

    /**
     * Maps Spotify Green to Gothic Kawaii Pink while preserving alpha, lightness and saturation.
     */
    public static int map(int color) {
        if (!isStockGreen(color)) {
            return color;
        }

        int targetAccent = SpotiMi.getAccentColor();
        if (targetAccent == STOCK_GREEN) {
            return color;
        }

        int alpha = Color.alpha(color);
        float[] hsv = new float[3];
        Color.colorToHSV(color, hsv);

        float[] refHsv = new float[3];
        Color.colorToHSV(STOCK_GREEN, refHsv);

        float[] tgtHsv = new float[3];
        Color.colorToHSV(targetAccent, tgtHsv);

        // Shift hue
        float deltaH = tgtHsv[0] - refHsv[0];
        float newH = (hsv[0] + deltaH) % 360.0f;
        if (newH < 0.0f) newH += 360.0f;

        // Proportional saturation & value
        float scaleS = refHsv[1] > 0 ? tgtHsv[1] / refHsv[1] : 1.0f;
        float scaleV = refHsv[2] > 0 ? tgtHsv[2] / refHsv[2] : 1.0f;

        float newS = Math.max(0.0f, Math.min(1.0f, hsv[1] * scaleS));
        float newV = Math.max(0.0f, Math.min(1.0f, hsv[2] * scaleV));

        return Color.HSVToColor(alpha, new float[]{newH, newS, newV});
    }

    /**
     * Hook for Resources.getColor(int id).
     */
    public static int hookColor(int resolvedColor) {
        return map(resolvedColor);
    }
}
