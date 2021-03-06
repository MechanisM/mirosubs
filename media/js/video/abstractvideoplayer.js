// Universal Subtitles, universalsubtitles.org
// 
// Copyright (C) 2010 Participatory Culture Foundation
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see 
// http://www.gnu.org/licenses/agpl-3.0.html.

goog.provide('mirosubs.video.AbstractVideoPlayer');

/**
 * Abstract base class for video player implementations. Any video player 
 * used with MiroSubs must implement the abstract methods defined by this 
 * class.
 * @constructor
 */
mirosubs.video.AbstractVideoPlayer = function(videoSource) {
    goog.ui.Component.call(this);
    this.videoSource_ = videoSource;
    this.noUpdateEvents_ = false;
    this.dimensionsKnown_ = false;
    this.isLoadingStopped_ = false;
    /**
     * If the video's loading is stopped (i.e., it is no longer buffering),
     * we may have had to alter the video source or playhead time to force
     * the buffering to actually cease.  While stopped, this variable will
     * store the playhead time we were previously at, so it can be restored.
     * @type{number}
     */
    this.storedPlayheadTime_ = 0;
    mirosubs.video.AbstractVideoPlayer.players.push(this);
};
goog.inherits(mirosubs.video.AbstractVideoPlayer, goog.ui.Component);
mirosubs.video.AbstractVideoPlayer.PROGRESS_INTERVAL = 500;
mirosubs.video.AbstractVideoPlayer.TIMEUPDATE_INTERVAL = 80;

mirosubs.video.AbstractVideoPlayer.logger_ = 
    goog.debug.Logger.getLogger('AbstractVideoPlayer');

mirosubs.video.AbstractVideoPlayer.players = [];

/**
 *
 * Used for flash-based video players that don't have a size specified.
 */
mirosubs.video.AbstractVideoPlayer.DEFAULT_SIZE = new goog.math.Size(480, 360);
/**
 *
 * Used for all video players in the dialog.
 */
mirosubs.video.AbstractVideoPlayer.DIALOG_SIZE = new goog.math.Size(400, 300);


mirosubs.video.AbstractVideoPlayer.prototype.getPlayheadFn = function() {
    return goog.bind(this.getPlayheadTime, this);
};
mirosubs.video.AbstractVideoPlayer.prototype.isPaused = function() {
    if (this.isLoadingStopped_)
	throw new "can't check if paused, loading is stopped";
    return this.isPausedInternal();
};
mirosubs.video.AbstractVideoPlayer.prototype.isPausedInternal = goog.abstractMethod;
mirosubs.video.AbstractVideoPlayer.prototype.isPlaying = function() {
    if (this.isLoadingStopped_)
	throw new "can't check if playing, loading is stopped";
    return this.isPlayingInternal();
};
mirosubs.video.AbstractVideoPlayer.prototype.isPlayingInternal = goog.abstractMethod;
mirosubs.video.AbstractVideoPlayer.prototype.videoEnded = function() {
    if (this.isLoadingStopped_)
	throw new "can't check if video ended, loading is stopped";
    return this.videoEndedInternal();
};
mirosubs.video.AbstractVideoPlayer.prototype.videoEndedInternal = goog.abstractMethod;
mirosubs.video.AbstractVideoPlayer.prototype.play = function(opt_suppressEvent) {
    if (this.isLoadingStopped_)
	throw new "can't play, loading is stopped";
    if (!opt_suppressEvent)
        this.dispatchEvent(
            mirosubs.video.AbstractVideoPlayer.EventType.PLAY_CALLED);
    this.playInternal();
};
mirosubs.video.AbstractVideoPlayer.prototype.playInternal = goog.abstractMethod;
mirosubs.video.AbstractVideoPlayer.prototype.pause = function(opt_suppressEvent) {
    if (this.isLoadingStopped_)
	throw new "can't pause, loading is stopped";
    if (!opt_suppressEvent)
        this.dispatchEvent(
            mirosubs.video.AbstractVideoPlayer.EventType.PAUSE_CALLED);
    this.pauseInternal();
};
mirosubs.video.AbstractVideoPlayer.prototype.pauseInternal = goog.abstractMethod;
mirosubs.video.AbstractVideoPlayer.prototype.togglePause = function() {
    if (this.isLoadingStopped_)
	throw new "can't toggle pause, loading is stopped";

    if (!this.isPlaying())
        this.play();
    else
        this.pause();
};
mirosubs.video.AbstractVideoPlayer.prototype.isLoadingStopped = function() {
  return this.isLoadingStopped_;  
};
/**
 * @protected
 */
mirosubs.video.AbstractVideoPlayer.prototype.setLoadingStopped = function(isLoadingStopped) {
  this.isLoadingStopped_ = isLoadingStopped;  
};
mirosubs.video.AbstractVideoPlayer.prototype.stopLoading = function() {
    if (!this.isLoadingStopped_) {
	this.pause();
	this.storedPlayheadTime_ = this.getPlayheadTime();
	if (this.stopLoadingInternal()) {
	    this.isLoadingStopped_ = true;
	}
    }
};
mirosubs.video.AbstractVideoPlayer.prototype.stopLoadingInternal = goog.abstractMethod;
mirosubs.video.AbstractVideoPlayer.prototype.resumeLoading = function() {
    if (this.isLoadingStopped_) {
	this.resumeLoadingInternal(this.storedPlayheadTime_);
	this.storedPlayheadTime_ = null;
    }
};
mirosubs.video.AbstractVideoPlayer.prototype.resumeLoadingInternal = function(playheadTime) {
    goog.abstractMethod();
};
/**
 * @protected
 * Must be called by subclasses once they know their dimensions.
 */
mirosubs.video.AbstractVideoPlayer.prototype.setDimensionsKnownInternal = function() {
    this.dimensionsKnown_ = true;
    this.dispatchEvent(
        mirosubs.video.AbstractVideoPlayer.EventType.DIMENSIONS_KNOWN);
};
mirosubs.video.AbstractVideoPlayer.prototype.areDimensionsKnown = function() {
    return this.dimensionsKnown_;
};
mirosubs.video.AbstractVideoPlayer.prototype.getPlayheadTime = function() {
    if (this.isLoadingStopped_)
	return this.storedPlayheadTime_;
    return this.getPlayheadTimeInternal();
};
mirosubs.video.AbstractVideoPlayer.prototype.getPlayheadTimeInternal = goog.abstractMethod;
/**
 * 
 *
 */
mirosubs.video.AbstractVideoPlayer.prototype.playWithNoUpdateEvents = 
    function(timeToStart, secondsToPlay) 
{
    this.noUpdateEvents_ = true;
    if (this.noUpdatePreTime_ == null)
        this.noUpdatePreTime_ = this.getPlayheadTime();
    this.setPlayheadTime(timeToStart);
    this.play();
    this.noUpdateStartTime_ = timeToStart;
    this.noUpdateEndTime_ = timeToStart + secondsToPlay;
};
/**
 * @protected
 */
mirosubs.video.AbstractVideoPlayer.prototype.dispatchEndedEvent = function() {
    this.dispatchEvent(mirosubs.video.AbstractVideoPlayer.EventType.PLAY_ENDED);
};
mirosubs.video.AbstractVideoPlayer.prototype.sendTimeUpdateInternal = 
    function() 
{
    if (!this.noUpdateEvents_)
        this.dispatchEvent(
            mirosubs.video.AbstractVideoPlayer.EventType.TIMEUPDATE);
    else {
        if (this.ignoreTimeUpdate_)
            return;
        if (this.getPlayheadTime() >= this.noUpdateEndTime_) {
            this.ignoreTimeUpdate_ = true;
            this.setPlayheadTime(this.noUpdatePreTime_);
            this.noUpdatePreTime_ = null;
            this.pause();
            this.ignoreTimeUpdate_ = false;
            this.noUpdateEvents_ = false;
        }
    }
}
/**
 * @returns {number} video duration in seconds. Returns 0 if duration isn't
 *     available yet.
 */
mirosubs.video.AbstractVideoPlayer.prototype.getDuration = goog.abstractMethod;
/**
 * @returns {int} Number of buffered ranges.
 */
mirosubs.video.AbstractVideoPlayer.prototype.getBufferedLength = goog.abstractMethod;
/**
 * @returns {number} Start of buffered range with index
 */
mirosubs.video.AbstractVideoPlayer.prototype.getBufferedStart = function(index) {
    goog.abstractMethod();
};
mirosubs.video.AbstractVideoPlayer.prototype.getBufferedEnd = function(index) {
    goog.abstractMethod();
};
/**
 * @return {number} 0.0 to 1.0
 */
mirosubs.video.AbstractVideoPlayer.prototype.getVolume = goog.abstractMethod;
/**
 * @return {Element} The video element. Used to check to see if a video on the 
 *     page has been wrapped in a player yet or not.
 */
mirosubs.video.AbstractVideoPlayer.prototype.getVideoElement = goog.abstractMethod;

/**
 * 
 * @param {number} volume A number between 0.0 and 1.0
 */
mirosubs.video.AbstractVideoPlayer.prototype.setVolume = function(volume) {
    goog.abstractMethod();
};
mirosubs.video.AbstractVideoPlayer.prototype.getVideoSource = function() {
    return this.videoSource_;
};
mirosubs.video.AbstractVideoPlayer.prototype.setPlayheadTime = function(playheadTime) {
    goog.abstractMethod();
};
/**
 *
 * @param {String} text Caption text to display in video. null for blank.
 */
mirosubs.video.AbstractVideoPlayer.prototype.showCaptionText = function(text) {
    mirosubs.video.AbstractVideoPlayer.logger_.info(
        'showing sub: ' + text);
    if (text == null || text == "") {
        if (this.captionElem_ != null) {
            goog.dom.removeNode(this.captionElem_);
            this.captionElem_ = null;
            if (this.captionBgElem_ != null) {
                goog.dom.removeNode(this.captionBgElem_);
                this.captionBgElem_ = null;
            }
        }
    }
    else
        this.setCaption_(
            goog.string.newLineToBr(goog.string.htmlEscape(text)),
            this.needsIFrame());
};

mirosubs.video.AbstractVideoPlayer.prototype.setCaption_ = 
    function(htmlText, needsIFrame) 
{
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var $s = goog.style;
    var videoOffsetParent = this.getElement().offsetParent;
    if (!videoOffsetParent)
        videoOffsetParent = goog.dom.getOwnerDocument(this.getElement()).body;
    var offsetPosition = $s.getPosition(this.getElement());
    var size = $s.getSize(this.getElement());
    var captionWidth = Math.min(400, size.width - 20);
    if (!this.captionElem_) {
        this.captionElem_ = $d('span', 'mirosubs-captionSpan');
        if (needsIFrame)
            mirosubs.style.setVisibility(this.captionElem_, false);
        goog.dom.appendChild(videoOffsetParent, this.captionElem_);
        mirosubs.style.setWidth(this.captionElem_, captionWidth);
        this.captionLeft_ = (offsetPosition.x + (size.width - captionWidth) / 2);
        mirosubs.style.setPosition(this.captionElem_, this.captionLeft_, null);
    }
    this.captionElem_.innerHTML = htmlText;
    var captionSize = goog.style.getSize(this.captionElem_);
    var captionTop = offsetPosition.y + size.height - captionSize.height - 40;
    mirosubs.style.setPosition(this.captionElem_, null, captionTop);

    if (needsIFrame) {
        if (!this.captionBgElem_) {
            this.captionBgElem_ = $d('iframe', 'mirosubs-captionSpanBg');
            mirosubs.style.setVisibility(this.captionBgElem_, false);
            this.getDomHelper().insertSiblingBefore(
                this.captionBgElem_, this.captionElem_);
        }
        $s.setPosition(this.captionBgElem_, this.captionLeft_, captionTop);
        $s.setSize(this.captionBgElem_, captionSize);
        mirosubs.style.setVisibility(this.captionBgElem_, true);
        mirosubs.style.setVisibility(this.captionElem_, true);
    }

};

/**
 * Override for video players that need to show an iframe behind captions for 
 * certain browsers (e.g. flash on linux/ff)
 * @protected
 */
mirosubs.video.AbstractVideoPlayer.prototype.needsIFrame = function() {
    return false;
};
/**
 *
 * @protected
 * @return {goog.math.Size} size of the video
 */
mirosubs.video.AbstractVideoPlayer.prototype.getVideoSize = goog.abstractMethod;

/**
 * Video player events
 * @enum {string}
 */
mirosubs.video.AbstractVideoPlayer.EventType = {
    /** dispatched when playback starts or resumes. */
    PLAY : 'videoplay',
    PLAY_CALLED : 'videoplaycalled',
    /** dispatched when the video finishes playing. */
    PLAY_ENDED : 'videoplayended',
    /** dispatched when playback is paused. */
    PAUSE : 'videopause',
    PAUSE_CALLED : 'videopausecalled',
    /** dispatched when media data is fetched */
    PROGRESS : 'videoprogress',
    /** 
     * dispatched when playhead time changes, either as a result 
     *  of normal playback or otherwise. 
     */
    TIMEUPDATE : 'videotimeupdate',
    /**
     * dispatched when video dimensions are known.
     */
    DIMENSIONS_KNOWN: 'dimensionsknown'
};
