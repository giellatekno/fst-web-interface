import './app.css';
import App from './App.svelte';
import {
    page_pathname,
    lang as current_lang,
    tool as current_tool,
} from "./lib/stores.js";

const app = new App({
    target: document.getElementById('app'),
});

window.addEventListener("click", function(ev) {
    // first find <a> tag that was clicked,
    // by walking up towards the root, looking for the first <a> tag we see
    let target = ev.target;
    for (;
         target && target.nodeName !== "A";
         target = target.parentNode);

    // we did not click an <a>, so return
    if (!target) return;

    // we did click an <a>, prevent default,
    // and update state of url
    ev.preventDefault();
    const href = new URL(target.href).pathname;
    window.history.pushState(null, "", href);
    page_pathname.set(href);
});

window.addEventListener("popstate", function(ev) {
    const path = window.location.pathname;
    page_pathname.set(path);
});

export default app;
