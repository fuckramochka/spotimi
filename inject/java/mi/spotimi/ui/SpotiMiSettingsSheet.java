package mi.spotimi.ui;

import android.app.Dialog;
import android.content.Context;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.widget.CompoundButton;
import android.widget.FrameLayout;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import mi.spotimi.Palette;
import mi.spotimi.SpotiMi;

/**
 * In-App Gothic Kawaii Settings Sheet.
 * Built with standard Android widgets to guarantee zero external dependency issues.
 */
public class SpotiMiSettingsSheet extends Dialog {

    public SpotiMiSettingsSheet(Context context) {
        super(context);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);

        Window window = getWindow();
        if (window != null) {
            window.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            window.setGravity(Gravity.BOTTOM);
            GradientDrawable bg = new GradientDrawable();
            bg.setColor(0xFF141216); // Deep gothic black-rose background
            bg.setCornerRadii(new float[]{42, 42, 42, 42, 0, 0, 0, 0});
            window.setBackgroundDrawable(bg);
            window.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
            window.setDimAmount(0.65f);
        }

        setContentView(buildView());
    }

    private View buildView() {
        Context ctx = getContext();
        int accent = SpotiMi.getAccentColor();

        LinearLayout root = new LinearLayout(ctx);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(14), dp(20), dp(24));

        // Drag handle pill
        View handle = new View(ctx);
        GradientDrawable handleBg = new GradientDrawable();
        handleBg.setColor(0x44FFFFFF);
        handleBg.setCornerRadius(dp(3));
        LinearLayout.LayoutParams handleLp = new LinearLayout.LayoutParams(dp(44), dp(5));
        handleLp.gravity = Gravity.CENTER_HORIZONTAL;
        handleLp.bottomMargin = dp(16);
        handle.setLayoutParams(handleLp);
        handle.setBackground(handleBg);
        root.addView(handle);

        // Header Title
        TextView title = new TextView(ctx);
        title.setText("Spoti Mi");
        title.setTextSize(22);
        title.setTextColor(accent);
        title.setTypeface(null, android.graphics.Typeface.BOLD);
        root.addView(title);

        // Subtitle
        TextView sub = new TextView(ctx);
        sub.setText("Gothic Kawaii Edition • v" + SpotiMi.VERSION);
        sub.setTextSize(12);
        sub.setTextColor(0xFF888888);
        LinearLayout.LayoutParams subLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        subLp.bottomMargin = dp(16);
        sub.setLayoutParams(subLp);
        root.addView(sub);

        // Scroll container
        ScrollView scroll = new ScrollView(ctx);
        LinearLayout content = new LinearLayout(ctx);
        content.setOrientation(LinearLayout.VERTICAL);

        // Section: Core Features
        addSectionHeader(content, "★ РЕЖИМИ ВІДТВОРЕННЯ");
        addToggle(content, "Безлімітні пропуски", "Зняття обмеження 6 скіпів на годину", SpotiMi.KEY_UNLIMITED_SKIPS, SpotiMi.isUnlimitedSkipsEnabled());
        addToggle(content, "On-Demand (Вибір треків)", "Вимкнення примусового Shuffle-only", SpotiMi.KEY_ON_DEMAND, SpotiMi.isOnDemandEnabled());
        addToggle(content, "Перемотування (Seeking)", "Вільне пересування повзунка часу", SpotiMi.KEY_ALLOW_SEEK, SpotiMi.isSeekEnabled());
        addToggle(content, "Режим повтору", "Повтор окремого треку або всього списку", SpotiMi.KEY_ALLOW_REPEAT, SpotiMi.isRepeatEnabled());

        addSectionHeader(content, "★ МЕДІА ТА БЛОКУВАННЯ");
        addToggle(content, "Блокування реклами", "Повне вирізання аудіо, відео та банерів", SpotiMi.KEY_BLOCK_ADS, SpotiMi.isAdBlockEnabled());
        addToggle(content, "Canvas та Тексти (Lyrics)", "Увімкнення відео-заставок і тексту пісень", SpotiMi.KEY_CANVAS_LYRICS, SpotiMi.isCanvasLyricsEnabled());
        addToggle(content, "Чистий інтерфейс", "Приховування кнопок «Купити Premium» та промо", SpotiMi.KEY_CLEAN_UI, SpotiMi.isCleanUiEnabled());

        addSectionHeader(content, "★ ПАЛІТРА АКЦЕНТУ");
        addThemeSelector(content);

        scroll.addView(content);
        root.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(420)));

        return root;
    }

    private void addSectionHeader(LinearLayout container, String text) {
        TextView tv = new TextView(getContext());
        tv.setText(text);
        tv.setTextSize(11);
        tv.setTextColor(0xFFFA58B6);
        tv.setTypeface(null, android.graphics.Typeface.BOLD);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dp(14);
        lp.bottomMargin = dp(6);
        tv.setLayoutParams(lp);
        container.addView(tv);
    }

    private void addToggle(LinearLayout container, String label, String desc, final String prefKey, boolean currentVal) {
        Context ctx = getContext();
        LinearLayout row = new LinearLayout(ctx);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setPadding(0, dp(10), 0, dp(10));

        LinearLayout textCol = new LinearLayout(ctx);
        textCol.setOrientation(LinearLayout.VERTICAL);
        LinearLayout.LayoutParams textColLp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1.0f);
        textCol.setLayoutParams(textColLp);

        TextView labelTv = new TextView(ctx);
        labelTv.setText(label);
        labelTv.setTextSize(15);
        labelTv.setTextColor(0xFFEEEEEE);
        textCol.addView(labelTv);

        TextView descTv = new TextView(ctx);
        descTv.setText(desc);
        descTv.setTextSize(12);
        descTv.setTextColor(0xFF888888);
        textCol.addView(descTv);

        Switch sw = new Switch(ctx);
        sw.setChecked(currentVal);
        sw.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                SpotiMi.setBoolean(prefKey, isChecked);
            }
        });

        row.addView(textCol);
        row.addView(sw);
        container.addView(row);
    }

    private void addThemeSelector(LinearLayout container) {
        Context ctx = getContext();
        HorizontalScrollView hscroll = new HorizontalScrollView(ctx);
        LinearLayout paletteRow = new LinearLayout(ctx);
        paletteRow.setOrientation(LinearLayout.HORIZONTAL);
        paletteRow.setPadding(0, dp(8), 0, dp(8));

        addThemeColorPill(paletteRow, "Gothic Kawaii Pink", SpotiMi.COLOR_GOTHIC_KAWAII_PINK);
        addThemeColorPill(paletteRow, "Sweet Sakura", SpotiMi.COLOR_SWEET_SAKURA);
        addThemeColorPill(paletteRow, "Cyber Magenta", SpotiMi.COLOR_CYBER_MAGENTA);
        addThemeColorPill(paletteRow, "Spotify Green", SpotiMi.COLOR_SPOTIFY_GREEN);

        hscroll.addView(paletteRow);
        container.addView(hscroll);
    }

    private void addThemeColorPill(LinearLayout row, final String name, final int color) {
        Context ctx = getContext();
        TextView pill = new TextView(ctx);
        pill.setText(name);
        pill.setTextSize(12);
        pill.setTextColor(0xFFFFFFFF);
        pill.setPadding(dp(12), dp(6), dp(12), dp(6));

        GradientDrawable gd = new GradientDrawable();
        gd.setColor(color);
        gd.setCornerRadius(dp(16));
        pill.setBackground(gd);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.rightMargin = dp(10);
        pill.setLayoutParams(lp);

        pill.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                SpotiMi.setAccentColor(color);
                dismiss();
            }
        });

        row.addView(pill);
    }

    private int dp(int value) {
        float density = getContext().getResources().getDisplayMetrics().density;
        return (int) (value * density + 0.5f);
    }
}
