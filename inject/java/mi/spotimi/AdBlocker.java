package mi.spotimi;

import android.util.Log;
import java.util.ArrayList;
import java.util.List;

/**
 * AdBlocker for Spoti Mi.
 * 
 * Intercepts audio ads, sponsored interstitial videos, and banner placements.
 */
public final class AdBlocker {
    private static final String TAG = "SpotiMi-AdBlocker";
    public static final String AD_URI_PREFIX = "spotify:ad:";

    private AdBlocker() {}

    /**
     * Checks if a track URI or context is an advertisement.
     */
    public static boolean isAdUri(String uri) {
        return uri != null && (uri.startsWith(AD_URI_PREFIX) || uri.contains(":ad:"));
    }

    /**
     * Intercepts isAd() method checks on Track objects.
     */
    public static boolean isAd(Object track, boolean original) {
        if (!SpotiMi.isAdBlockEnabled()) {
            return original;
        }
        // Always report non-ad to UI/Engine
        return false;
    }

    /**
     * Intercepts AdBreak and AdSlot scheduling.
     */
    public static boolean shouldScheduleAdBreak(boolean original) {
        if (SpotiMi.isAdBlockEnabled()) {
            return false;
        }
        return original;
    }

    /**
     * Filters ad tracks out of incoming playback queues.
     */
    @SuppressWarnings("rawtypes")
    public static List filterQueue(List originalQueue) {
        if (!SpotiMi.isAdBlockEnabled() || originalQueue == null) {
            return originalQueue;
        }
        List clean = new ArrayList();
        for (Object item : originalQueue) {
            if (item != null) {
                String uri = extractUri(item);
                if (isAdUri(uri)) {
                    Log.d(TAG, "Blocked audio ad track from queue: " + uri);
                    continue;
                }
            }
            clean.add(item);
        }
        return clean;
    }

    private static String extractUri(Object item) {
        try {
            return (String) item.getClass().getMethod("getUri").invoke(item);
        } catch (Throwable ignored) {
            return null;
        }
    }
}
