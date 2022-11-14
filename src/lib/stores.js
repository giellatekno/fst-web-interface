import {
    writable,
    derived,
    get,
} from "svelte/store";

export const page_pathname = writable(
    new URL(window.location).pathname
);

// The language the user is exploring
export const lang = derived(
    page_pathname,
    $pn => $pn.split("/")[1]
);

export const tool = derived(
    page_pathname,
    $pn => $pn.split("/")[2] ?? ""
);

//export const lang = make_lang();

// The tool the user is exploring
//export const tool = make_selected_tool();

// Manually keeping track of and updating
// the pathname of the page url.
/*
export const page_pathname = derived(
    [lang, tool],
    ([$lang, $tool]) => {
        if (!$lang) return `/`;
        if (!$tool) return `/${$lang}`;
        return `/${$lang}/${tool}`;
    }
);
*/

// factory functions that makes new stores.
// doing this to be able to override the
// set() method, because we want to have
// custom logic triggered when these stores
// gets set

function make_lang() {
    const inner = writable("");

    function set(value) {
        inner.set(value);
        window.history.pushState(
            null,
            "",
            `/${value}`,
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
        const tlang = get(lang);
        window.history.pushState(
            null,
            "",
            `/${tlang}/${value}`
        );
    }

    return {
        subscribe: inner.subscribe,
        set,
    };
}
