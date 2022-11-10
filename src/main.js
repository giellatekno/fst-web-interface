import './app.css';
import App from './App.svelte';

import {
    addMessages,
    init,
} from 'svelte-intl-precompile';
import nob from "../locales/nob.json";
import eng from "../locales/eng.json";
addMessages('nob', nob);
addMessages('eng', eng);

import {
    ui_lang,
    target_lang,
    selected_tool,
} from "./lib/stores.js";

const app = new App({
    target: document.getElementById('app'),
    props: {
        page: "/"
    }
});

init({
    fallbackLocale: 'nob',
    initialLocale: 'nob',
});

window.addEventListener("click", function(ev) {
    if (ev.target.nodeName !== "A") return;
    ev.preventDefault();
    const href = new URL(ev.target.href).pathname;
    window.history.pushState(null, "", href);
    app.$set({ page: href });
});

window.addEventListener("popstate", function(ev) {
    const path = window.location.pathname;
    console.debug("popstate event. path= ", path);
    const [_, a, b, c] = page.split("/");
    ui_lang.set(a);
    target_lang.set(b);
    selected_tool.set(c);
});

export default app;
