import './app.css';
import App from './App.svelte';
import { lang, tool } from "./lib/stores.js";
import { locale } from "./lib/locales.js";

const app = new App({
    target: document.getElementById('app'),
});

window.addEventListener("click", function(ev) {
    if (ev.target.nodeName !== "A") return;
    ev.preventDefault();
    const href = new URL(ev.target.href).pathname;
    const url = `${get(locale)}/${href}`;
    window.history.pushState(null, "", url);
});

window.addEventListener("popstate", function(ev) {
    const path = window.location.pathname;
    console.debug("popstate event. path= ", path);
    const [_, a, b, c] = path.split("/");
    locale.set(a);
    lang.set(b);
    selected_tool.set(c);
});

export default app;
