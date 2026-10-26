package mi.spotimi;

import android.util.Log;

/**
 * ProductState & FeatureFlag hooks.
 * 
 * Spotify fetches account configuration via RemoteConfig / ProductState.
 * Overriding these values tells the entire application that it operates
 * with Premium privileges:
 * - type: "premium"
 * - streaming-rules: "" (removes shuffle enforcement)
 * - can_seek: "1" (enables scrubber)
 * - on-demand: "1" (enables direct song selection)
 * - ads: "0" (disables ad injection)
 * - canvaz.enabled: "true" (enables video canvas loops)
 * - lyrics.feature-enabled: "true" (enables synchronized lyrics)
 */
public final class ProductStateHooks {
    private static final String TAG = "SpotiMi-ProductState";

    private ProductStateHooks() {}

    /**
     * Intercepts String queries on ProductState.
     */
    public static String get(Object productState, String key, String fallback) {
        if (key != null) {
            switch (key) {
                case "type":
                case "license":
                    return "premium";

                case "streaming-rules":
                    return SpotiMi.isOnDemandEnabled() ? "" : fallback;

                case "can_seek":
                    return SpotiMi.isSeekEnabled() ? "1" : fallback;

                case "on-demand":
                    return SpotiMi.isOnDemandEnabled() ? "1" : fallback;

                case "ads":
                    return SpotiMi.isAdBlockEnabled() ? "0" : fallback;

                case "pause_after":
                    return "0";

                case "canvaz.enabled":
                    return SpotiMi.isCanvasLyricsEnabled() ? "1" : fallback;

                case "lyrics.feature-enabled":
                    return SpotiMi.isCanvasLyricsEnabled() ? "1" : fallback;
            }
        }
        return realGet(productState, key, fallback);
    }

    /**
     * Intercepts single-parameter String queries.
     */
    public static String get(Object productState, String key) {
        return get(productState, key, "");
    }

    /**
     * Intercepts boolean feature flag queries.
     */
    public static boolean getBoolean(Object productState, String key, boolean fallback) {
        if (key != null) {
            switch (key) {
                case "ads":
                case "ad_formats":
                case "ad_rules":
                    return SpotiMi.isAdBlockEnabled() ? false : fallback;

                case "can_seek":
                    return SpotiMi.isSeekEnabled() ? true : fallback;

                case "on_demand":
                case "on_demand_enabled":
                    return SpotiMi.isOnDemandEnabled() ? true : fallback;

                case "shuffle_restricted":
                    return SpotiMi.isOnDemandEnabled() ? false : fallback;

                case "canvaz.enabled":
                case "canvas.enabled":
                    return SpotiMi.isCanvasLyricsEnabled() ? true : fallback;

                case "lyrics.feature-enabled":
                case "lyrics.enabled":
                    return SpotiMi.isCanvasLyricsEnabled() ? true : fallback;

                case "premium":
                case "is_premium":
                    return true;
            }
        }
        return realGetBoolean(productState, key, fallback);
    }

    private static String realGet(Object obj, String key, String fallback) {
        if (obj == null) return fallback;
        try {
            return (String) obj.getClass().getMethod("get", String.class, String.class)
                    .invoke(obj, key, fallback);
        } catch (Throwable t) {
            try {
                String val = (String) obj.getClass().getMethod("get", String.class).invoke(obj, key);
                return val != null ? val : fallback;
            } catch (Throwable ignored) {
                return fallback;
            }
        }
    }

    private static boolean realGetBoolean(Object obj, String key, boolean fallback) {
        if (obj == null) return fallback;
        try {
            return (Boolean) obj.getClass().getMethod("getBoolean", String.class, boolean.class)
                    .invoke(obj, key, fallback);
        } catch (Throwable t) {
            return fallback;
        }
    }
}
