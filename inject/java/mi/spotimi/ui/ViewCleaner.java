package mi.spotimi.ui;

import android.view.View;
import android.view.ViewGroup;
import mi.spotimi.SpotiMi;

/**
 * View cleaner for Spoti Mi.
 * 
 * Hides "Get Premium" nag screens, upsell banners, and audiobook promo carousels.
 */
public final class ViewCleaner {
    private static final String[] HIDE_PATTERNS = {
        "upsell",
        "premium_banner",
        "upgrade_button",
        "buy_premium",
        "ad_slot",
        "banner_container",
        "promo_badge"
    };

    private ViewCleaner() {}

    /**
     * Inspects a view during inflation or binding and collapses it if it matches an upsell element.
     */
    public static void clean(View view) {
        if (view == null || !SpotiMi.isCleanUiEnabled()) {
            return;
        }

        try {
            int id = view.getId();
            if (id != View.NO_ID && view.getResources() != null) {
                String entryName = view.getResources().getResourceEntryName(id).toLowerCase();
                for (String pattern : HIDE_PATTERNS) {
                    if (entryName.contains(pattern)) {
                        collapse(view);
                        return;
                    }
                }
            }
        } catch (Throwable ignored) {}
    }

    private static void collapse(View view) {
        view.setVisibility(View.GONE);
        ViewGroup.LayoutParams lp = view.getLayoutParams();
        if (lp != null) {
            lp.height = 0;
            lp.width = 0;
            view.setLayoutParams(lp);
        }
    }
}
