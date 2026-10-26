package mi.spotimi;

import android.app.Activity;
import android.app.Application;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.view.Window;
import android.widget.Toast;
import mi.spotimi.ui.SpotiMiSettingsSheet;

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
 * 8. Gothic Blood Rose (#B81B34) and custom live theme switcher
 * 9. AMOLED Pure Black (#000000) Mode
 * 10. In-App GitHub Auto-Updater
 */
public final class SpotiMi {
    public static final String TAG = "SpotiMi";
    public static final String VERSION = "1.0.1";
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
    public static final String KEY_AMOLED_BLACK = "amoled_pure_black";
    public static final String KEY_HINT_SHOWN = "hint_3finger_shown";

    // Themes
    public static final int COLOR_GOTHIC_BLOOD_ROSE = 0xFFB81B34; // Deep Velvet Gothic Blood Rose (non-neon)
    public static final int COLOR_SWEET_SAKURA = 0xFFFF70A6;      // Soft Pastel Sakura Pink
    public static final int COLOR_CYBER_MAGENTA = 0xFFE056FD;     // Cyberpunk Magenta
    public static final int COLOR_DARK_RUBY = 0xFFA61C3C;         // Dark Ruby Wine
    public static final int COLOR_SPOTIFY_GREEN = 0xFF1DB954;     // Stock Spotify Green

    private static volatile Context sContext;
    private static volatile SharedPreferences sPrefs;
    private static volatile Activity sCurrentActivity;

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
            Log.i(TAG, "★ Spoti Mi initialized [v" + VERSION + "] — Gothic Edition");

            if (sContext instanceof Application) {
                ((Application) sContext).registerActivityLifecycleCallbacks(new Application.ActivityLifecycleCallbacks() {
                    @Override
                    public void onActivityCreated(Activity activity, Bundle savedInstanceState) {
                        onActivityCreate(activity);
                    }
                    @Override public void onActivityStarted(Activity activity) {}
                    @Override public void onActivityResumed(Activity activity) { sCurrentActivity = activity; }
                    @Override public void onActivityPaused(Activity activity) {}
                    @Override public void onActivityStopped(Activity activity) {}
                    @Override public void onActivitySaveInstanceState(Activity activity, Bundle outState) {}
                    @Override public void onActivityDestroyed(Activity activity) {
                        if (sCurrentActivity == activity) sCurrentActivity = null;
                    }
                });
            }
        }
    }

    /**
     * Called whenever an Activity is created. Attaches the 3-finger gesture listener
     * to open Spoti Mi Settings from anywhere in the app.
     */
    public static void onActivityCreate(final Activity activity) {
        if (activity == null) return;
        sCurrentActivity = activity;
        init(activity);

        // Check for updates on startup
        Updater.start(activity);

        // Attach 3-finger tap listener to window decor view
        try {
            final Window window = activity.getWindow();
            if (window != null) {
                final View decor = window.getDecorView();
                if (decor != null) {
                    decor.setOnTouchListener(new View.OnTouchListener() {
                        private long lastTrigger = 0;

                        @Override
                        public boolean onTouch(View v, MotionEvent event) {
                            if (event.getPointerCount() >= 3 && event.getActionMasked() == MotionEvent.ACTION_POINTER_DOWN) {
                                long now = System.currentTimeMillis();
                                if (now - lastTrigger > 1200) {
                                    lastTrigger = now;
                                    openSettings(activity);
                                    return true;
                                }
                            }
                            return false;
                        }
                    });
                }
            }
        } catch (Throwable t) {
            Log.w(TAG, "Failed to attach gesture listener", t);
        }

        // Show welcome hint once
        SharedPreferences p = getPrefs();
        if (p != null && !p.getBoolean(KEY_HINT_SHOWN, false)) {
            p.edit().putBoolean(KEY_HINT_SHOWN, true).apply();
            new Handler(Looper.getMainLooper()).postDelayed(new Runnable() {
                @Override
                public void run() {
                    try {
                        Toast.makeText(activity, "★ Spoti Mi: Натисніть 3 пальцями на екран для відкриття меню налаштувань", Toast.LENGTH_LONG).show();
                    } catch (Throwable ignored) {}
                }
            }, 3500);
        }
    }

    public static void openSettings(Activity activity) {
        if (activity != null && !activity.isFinishing()) {
            new SpotiMiSettingsSheet(activity).show();
        }
    }

    public static Context getContext() {
        return sContext;
    }

    public static Activity getCurrentActivity() {
        return sCurrentActivity;
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

    public static boolean isAmoledBlackEnabled() {
        SharedPreferences p = getPrefs();
        return p == null || p.getBoolean(KEY_AMOLED_BLACK, true);
    }

    public static int getAccentColor() {
        SharedPreferences p = getPrefs();
        return p != null ? p.getInt(KEY_ACCENT_COLOR, COLOR_GOTHIC_BLOOD_ROSE) : COLOR_GOTHIC_BLOOD_ROSE;
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
