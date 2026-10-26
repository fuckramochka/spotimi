package mi.spotimi;

import android.app.Application;
import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

/**
 * Spoti Mi — Core mod configuration & state manager.
 * 
 * Features:
 * 1. Unlimited skips (no 6-skip hourly cap)
 * 2. On-Demand track playback (free choice of song, disables forced shuffle)
 * 3. Complete ad-blocking (audio, video, display banners)
 * 4. Free seeking & scrubbing
 * 5. Track & context repeat modes
 * 6. Video Canvas & synchronized Lyrics
 * 7. Clean UI (hidden upsell nag buttons & banners)
 * 8. Gothic Kawaii Pink accent theme (#FF2A85)
 */
public final class SpotiMi {
    public static final String TAG = "SpotiMi";
    public static final String VERSION = "1.0.0-kawaii";
    public static final String PREFS_NAME = "spoti_mi_preferences";

    // Feature preference keys
    public static final String KEY_UNLIMITED_SKIPS = "unlimited_skips";
    public static final String KEY_ON_DEMAND = "on_demand_play";
    public static final String KEY_BLOCK_ADS = "block_all_ads";
    public static final String KEY_ALLOW_SEEK = "allow_seeking";
    public static final String KEY_ALLOW_REPEAT = "allow_repeat";
    public static final String KEY_CANVAS_LYRICS = "canvas_and_lyrics";
    public static final String KEY_CLEAN_UI = "clean_interface";
    public static final String KEY_ACCENT_COLOR = "accent_color";

    // Theme: Gothic Kawaii Pink (#FF2A85)
    public static final int COLOR_GOTHIC_KAWAII_PINK = 0xFFFF2A85;
    public static final int COLOR_SWEET_SAKURA = 0xFFFF70A6;
    public static final int COLOR_CYBER_MAGENTA = 0xFFE056FD;
    public static final int COLOR_SPOTIFY_GREEN = 0xFF1DB954;

    private static volatile Context sContext;
    private static volatile SharedPreferences sPrefs;

    private SpotiMi() {}

    /**
     * Entry hook called at application startup.
     */
    public static void init(Context context) {
        if (sContext == null && context != null) {
            sContext = context.getApplicationContext() != null 
                    ? context.getApplicationContext() 
                    : context;
            sPrefs = sContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
            Log.i(TAG, "★ Spoti Mi initialized [v" + VERSION + "] — Gothic Kawaii Edition");
        }
    }

    public static Context getContext() {
        return sContext;
    }

    public static SharedPreferences getPrefs() {
        if (sPrefs == null && sContext != null) {
            sPrefs = sContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        }
        return sPrefs;
    }

    // ------------------------------------------------------------------------
    // Feature Checks
    // ------------------------------------------------------------------------

    public static boolean isUnlimitedSkipsEnabled() {
        SharedPreferences p = getPrefs();
        return p == null || p.getBoolean(KEY_UNLIMITED_SKIPS, true);
    }

    public static boolean isOnDemandEnabled() {
        SharedPreferences p = getPrefs();
        return p == null || p.getBoolean(KEY_ON_DEMAND, true);
    }

    public static boolean isAdBlockEnabled() {
        SharedPreferences p = getPrefs();
        return p == null || p.getBoolean(KEY_BLOCK_ADS, true);
    }

    public static boolean isSeekEnabled() {
        SharedPreferences p = getPrefs();
        return p == null || p.getBoolean(KEY_ALLOW_SEEK, true);
    }

    public static boolean isRepeatEnabled() {
        SharedPreferences p = getPrefs();
        return p == null || p.getBoolean(KEY_ALLOW_REPEAT, true);
    }

    public static boolean isCanvasLyricsEnabled() {
        SharedPreferences p = getPrefs();
        return p == null || p.getBoolean(KEY_CANVAS_LYRICS, true);
    }

    public static boolean isCleanUiEnabled() {
        SharedPreferences p = getPrefs();
        return p == null || p.getBoolean(KEY_CLEAN_UI, true);
    }

    public static int getAccentColor() {
        SharedPreferences p = getPrefs();
        return p != null ? p.getInt(KEY_ACCENT_COLOR, COLOR_GOTHIC_KAWAII_PINK) : COLOR_GOTHIC_KAWAII_PINK;
    }

    public static void setBoolean(String key, boolean value) {
        SharedPreferences p = getPrefs();
        if (p != null) {
            p.edit().putBoolean(key, value).apply();
        }
    }

    public static void setAccentColor(int color) {
        SharedPreferences p = getPrefs();
        if (p != null) {
            p.edit().putInt(KEY_ACCENT_COLOR, color).apply();
        }
    }
}
