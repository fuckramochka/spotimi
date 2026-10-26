package mi.spotimi;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.Toast;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Locale;
import org.json.JSONObject;

/**
 * Spoti Mi Auto-Updater.
 * 
 * Fetches release information from GitHub:
 * https://raw.githubusercontent.com/fuckramochka/spotimi/main/version.json
 * 
 * Offers one-tap update download and installation via standard Android DownloadManager.
 */
public final class Updater {
    public static final String TAG = "SpotiMi-Updater";
    public static final String UPDATE_URL = "https://raw.githubusercontent.com/fuckramochka/spotimi/main/version.json";

    private static volatile boolean sChecked = false;
    private static volatile String sLatestVersion = "";
    private static volatile String sDownloadUrl = "";
    private static volatile String sNotes = "";

    private Updater() {}

    /**
     * Start automatic background check on application launch.
     */
    public static void start(final Context context) {
        if (sChecked || context == null) return;
        sChecked = true;

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Thread.sleep(3000); // Wait for initial UI to settle
                    check(context, false);
                } catch (Throwable ignored) {}
            }
        }).start();
    }

    /**
     * Check for updates.
     * @param context Application or Activity context.
     * @param byHand True if triggered manually from Settings.
     */
    public static void check(final Context context, final boolean byHand) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    URL url = new URL(UPDATE_URL);
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setConnectTimeout(8000);
                    conn.setReadTimeout(8000);
                    conn.setRequestProperty("User-Agent", "SpotiMi/" + SpotiMi.VERSION);

                    if (conn.getResponseCode() != 200) {
                        if (byHand) showToast(context, "Не вдалося отримати дані оновлення (" + conn.getResponseCode() + ")");
                        return;
                    }

                    BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        sb.append(line);
                    }
                    reader.close();

                    JSONObject json = new JSONObject(sb.toString());
                    sLatestVersion = json.optString("version", "");
                    sDownloadUrl = json.optString("url", "");

                    String lang = Locale.getDefault().getLanguage();
                    sNotes = json.optString("notes_" + lang, json.optString("notes", ""));

                    if (isNewer(sLatestVersion, SpotiMi.VERSION)) {
                        new Handler(Looper.getMainLooper()).post(new Runnable() {
                            @Override
                            public void run() {
                                showUpdateDialog(context, sLatestVersion, sDownloadUrl, sNotes);
                            }
                        });
                    } else if (byHand) {
                        showToast(context, "★ Spoti Mi v" + SpotiMi.VERSION + " — встановлена найновіша версія!");
                    }
                } catch (final Throwable e) {
                    Log.e(TAG, "Update check failed", e);
                    if (byHand) {
                        showToast(context, "Помилка перевірки оновлення: " + e.getMessage());
                    }
                }
            }
        }).start();
    }

    private static boolean isNewer(String latest, String current) {
        if (latest == null || latest.isEmpty() || current == null) return false;
        String l = latest.replaceAll("[^0-9.]", "");
        String c = current.replaceAll("[^0-9.]", "");
        return !l.equals(c) && !l.isEmpty();
    }

    public static void showUpdateDialog(final Context context, final String version, final String apkUrl, final String notes) {
        Activity activity = (context instanceof Activity) ? (Activity) context : null;
        if (activity == null && SpotiMi.getCurrentActivity() != null) {
            activity = SpotiMi.getCurrentActivity();
        }
        if (activity == null || activity.isFinishing()) return;

        AlertDialog.Builder builder = new AlertDialog.Builder(activity, AlertDialog.THEME_DEVICE_DEFAULT_DARK);
        builder.setTitle("★ Доступне оновлення Spoti Mi v" + version);
        builder.setMessage((notes.isEmpty() ? "Нова версія готова до встановлення!" : notes)
                + "\n\nБажаєте оновити додаток зараз?");

        builder.setPositiveButton("Оновити", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                downloadAndInstall(context, apkUrl, version);
            }
        });

        builder.setNeutralButton("GitHub Реліз", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                try {
                    Intent browser = new Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/fuckramochka/spotimi/releases"));
                    browser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    context.startActivity(browser);
                } catch (Throwable ignored) {}
            }
        });

        builder.setNegativeButton("Пізніше", null);
        builder.show();
    }

    public static void downloadAndInstall(Context context, String apkUrl, String version) {
        try {
            DownloadManager dm = (DownloadManager) context.getSystemService(Context.DOWNLOAD_SERVICE);
            if (dm == null) {
                Intent browser = new Intent(Intent.ACTION_VIEW, Uri.parse(apkUrl));
                browser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(browser);
                return;
            }

            String filename = "SpotiMi-v" + version + ".apk";
            DownloadManager.Request req = new DownloadManager.Request(Uri.parse(apkUrl))
                    .setTitle("Spoti Mi v" + version)
                    .setDescription("Завантаження нової версії Spoti Mi...")
                    .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                    .setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, filename)
                    .setMimeType("application/vnd.android.package-archive");

            dm.enqueue(req);
            showToast(context, "★ Завантаження оновлення розпочато! Перевірте панель сповіщень.");
        } catch (Throwable e) {
            Log.e(TAG, "Download failed", e);
            Intent browser = new Intent(Intent.ACTION_VIEW, Uri.parse(apkUrl));
            browser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(browser);
        }
    }

    private static void showToast(final Context context, final String text) {
        new Handler(Looper.getMainLooper()).post(new Runnable() {
            @Override
            public void run() {
                try {
                    Toast.makeText(context.getApplicationContext(), text, Toast.LENGTH_SHORT).show();
                } catch (Throwable ignored) {}
            }
        });
    }
}
