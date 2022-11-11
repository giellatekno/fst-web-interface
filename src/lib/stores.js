import {
    writable,
    derived,
    get,
} from "svelte/store";

import { locale } from "svelte-intl-precompile";

// The language the user is exploring
export const lang = make_lang();

// The tool the user is exploring
export const tool = make_selected_tool();

// Manually keeping track of and updating
// the pathname of the page url.
export const page_pathname = derived(
    [locale, lang, tool],
    ([$locale, $lang, $tool]) => {
        if (!$lang) return `/${locale}`;
        if (!$tool) return `/${locale}/${$lang}`;
        return `/${$locale}/${$lang}/${tool}`;
    }
);

// factory functions that makes new stores.
// doing this to be able to override the
// set() method, because we want to have
// custom logic triggered when these stores
// gets set

function make_ui_lang() {
    const path = window.location.pathname;
    let initial = "sme";
    if (path.length > 1) {
        const from_url = path.slice(1, 4);
        if (locales.includes(from_url)) {
            initial = from_url;
        } else {
            // silently ignore and choose
            // sme as default
        }
    }
    const inner = writable(initial);

    function set(value) {
        inner.set(value);
        const loc = get(locale);
        const tlang = get(lang);
        window.history.replaceState(
            null,
            "",
            `/${loc}/${tlang}`
        );
    }

    return {
        subscribe: inner.subscribe,
        set,
    };
}

function make_lang() {
    const inner = writable("");

    function set(value) {
        const loc = get(locale);
        inner.set(value);
        window.history.pushState(
            null,
            "",
            `/${loc}/${value}`,
        );
    }

    return {
        subscribe: inner.subscribe,
        set,
    };
}

function make_selected_tool() {
    const path = window.location.pathname.split("/");
    const [_, uilang, tlang, tool] = path;
    const inner = writable(tool ?? "");

    function set(value) {
        inner.set(value);
        const loc = get(locale);
        const tlang = get(lang);
        window.history.pushState(
            null,
            "",
            `/${loc}/${tlang}/${value}`
        );
    }

    return {
        subscribe: inner.subscribe,
        set,
    };
}
