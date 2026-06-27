// ==================================================
// PUBG BATTLE PREDICTOR — OPTIONAL JS HOOK
//
// IMPORTANT: every animation that used to live here
// (dust particles, plane flight, character drop, probability
// flashing) has been moved to pure CSS keyframes in
// styles.css. Pure CSS animations run the instant the markup
// is inserted into the DOM and need no script execution at
// all, which is what makes them reliable on Streamlit Cloud.
//
// This file used to rewrite every `document.` lookup to
// `window.parent.document.` so it could reach elements living
// on Streamlit's main page from inside this component's
// sandboxed iframe. That cross-iframe DOM access is exactly
// what was unreliable on Streamlit Cloud (timing, sandbox
// permissions, and load order all differ from localhost). So
// this script no longer touches the parent document at all —
// it is not required for anything in the app to work.
//
// It's kept only as a placeholder/hook in case a future
// same-iframe widget ever needs a small bit of JS. There is
// currently nothing for it to do.
// ==================================================

(function () {
    // Intentionally empty. All visual effects are CSS-driven.
})();
