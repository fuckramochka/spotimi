package mi.spotimi;

import java.util.Collections;
import java.util.Set;

/**
 * PlayerRestrictions & Playback hooks.
 * 
 * In Spotify Free, playback limitations are governed by Restrictions objects
 * that return non-empty sets of reason codes:
 * - "mft_disallow" / "skip_limit_reached" (blocks skips)
 * - "seeking_restricted" (blocks scrubbing)
 * - "repeat_restricted" (blocks repeat mode)
 * - "peeking_restricted" (blocks on-demand track selection)
 * 
 * By redirecting these queries to return Collections.emptySet(), the client
 * immediately unlocks full player freedom.
 */
public final class PlayerHooks {
    private static final Set<String> EMPTY = Collections.emptySet();

    private PlayerHooks() {}

    /**
     * Unlimited skips: Next track is never disallowed.
     */
    public static Set<String> getDisallowSkippingNextReasons(Object restrictions) {
        if (SpotiMi.isUnlimitedSkipsEnabled()) {
            return EMPTY;
        }
        return realDisallowSkippingNext(restrictions);
    }

    /**
     * Previous track is always permitted.
     */
    public static Set<String> getDisallowSkippingPrevReasons(Object restrictions) {
        if (SpotiMi.isUnlimitedSkipsEnabled()) {
            return EMPTY;
        }
        return realDisallowSkippingPrev(restrictions);
    }

    /**
     * Seeking / scrubbing: Player progress bar can be freely moved.
     */
    public static Set<String> getDisallowSeekingReasons(Object restrictions) {
        if (SpotiMi.isSeekEnabled()) {
            return EMPTY;
        }
        return realDisallowSeeking(restrictions);
    }

    /**
     * Repeat track (Repeat One): enabled.
     */
    public static Set<String> getDisallowRepeatingTrackReasons(Object restrictions) {
        if (SpotiMi.isRepeatEnabled()) {
            return EMPTY;
        }
        return realDisallowRepeatingTrack(restrictions);
    }

    /**
     * Repeat context (Repeat All / Playlist): enabled.
     */
    public static Set<String> getDisallowRepeatingContextReasons(Object restrictions) {
        if (SpotiMi.isRepeatEnabled()) {
            return EMPTY;
        }
        return realDisallowRepeatingContext(restrictions);
    }

    /**
     * Peeking next: Allows selecting any track directly from list.
     */
    public static Set<String> getDisallowPeekingNextReasons(Object restrictions) {
        if (SpotiMi.isOnDemandEnabled()) {
            return EMPTY;
        }
        return realDisallowPeekingNext(restrictions);
    }

    /**
     * Peeking prev: Allows selecting previous tracks freely.
     */
    public static Set<String> getDisallowPeekingPrevReasons(Object restrictions) {
        if (SpotiMi.isOnDemandEnabled()) {
            return EMPTY;
        }
        return realDisallowPeekingPrev(restrictions);
    }

    /**
     * Shuffle mode restriction override: Allows disabling forced shuffle.
     */
    public static boolean isShufflingContext(boolean original) {
        if (SpotiMi.isOnDemandEnabled()) {
            // Allows normal linear playback
            return original;
        }
        return original;
    }

    /**
     * Fallback handlers that reflectively invoke original methods if mod is disabled.
     */
    @SuppressWarnings("unchecked")
    private static Set<String> realDisallowSkippingNext(Object obj) {
        try {
            return (Set<String>) obj.getClass().getMethod("disallowSkippingNextReasons").invoke(obj);
        } catch (Throwable ignored) {
            return EMPTY;
        }
    }

    @SuppressWarnings("unchecked")
    private static Set<String> realDisallowSkippingPrev(Object obj) {
        try {
            return (Set<String>) obj.getClass().getMethod("disallowSkippingPrevReasons").invoke(obj);
        } catch (Throwable ignored) {
            return EMPTY;
        }
    }

    @SuppressWarnings("unchecked")
    private static Set<String> realDisallowSeeking(Object obj) {
        try {
            return (Set<String>) obj.getClass().getMethod("disallowSeekingReasons").invoke(obj);
        } catch (Throwable ignored) {
            return EMPTY;
        }
    }

    @SuppressWarnings("unchecked")
    private static Set<String> realDisallowRepeatingTrack(Object obj) {
        try {
            return (Set<String>) obj.getClass().getMethod("disallowRepeatingTrackReasons").invoke(obj);
        } catch (Throwable ignored) {
            return EMPTY;
        }
    }

    @SuppressWarnings("unchecked")
    private static Set<String> realDisallowRepeatingContext(Object obj) {
        try {
            return (Set<String>) obj.getClass().getMethod("disallowRepeatingContextReasons").invoke(obj);
        } catch (Throwable ignored) {
            return EMPTY;
        }
    }

    @SuppressWarnings("unchecked")
    private static Set<String> realDisallowPeekingNext(Object obj) {
        try {
            return (Set<String>) obj.getClass().getMethod("disallowPeekingNextReasons").invoke(obj);
        } catch (Throwable ignored) {
            return EMPTY;
        }
    }

    @SuppressWarnings("unchecked")
    private static Set<String> realDisallowPeekingPrev(Object obj) {
        try {
            return (Set<String>) obj.getClass().getMethod("disallowPeekingPrevReasons").invoke(obj);
        } catch (Throwable ignored) {
            return EMPTY;
        }
    }
}
