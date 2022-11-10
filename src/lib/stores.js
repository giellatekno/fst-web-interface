import {
    writable,
    derived,
    get,
} from "svelte/store";

// The user interface language
export const ui_lang = make_ui_lang();

// The language the user is exploring
export const target_lang = make_target_lang();

// The tool the user is exploring
export const selected_tool = make_selected_tool();

// Manually keeping track of and updating
// the pathname of the page url.
export const page_pathname = derived(
    [ui_lang, target_lang, selected_tool],
    ([$ui_lang, $target_lang, $tool]) => {
        if (!$ui_lang) {
            // no ui_lang, we must be at root
            return "/";
        }

        if (!$target_lang) {
            // no target_lang
            return `/${$ui_lang}`;
        }

        return `/${$ui_lang}/${$tool}`;
    }
);

derived(page_pathname, path => {
    console.log("in derived");
    //window.location
});


// factory functions that makes new stores.
// doing this to be able to override the
// set() method, because we want to have
// custom logic triggered when these stores
// gets set

function make_ui_lang() {
    const path = window.location.pathname;
    let initial = "sme";
    if (path.length > 1) {
        initial = path.slice(1, 4);
    }
    const inner = writable(initial);

    function set(value) {
        inner.set(value);
        const uilang = get(ui_lang);
        const tlang = get(target_lang);
        window.history.replaceState(
            null,
            "",
            `/${uilang}/${tlang}`
        );
    }

    return {
        subscribe: inner.subscribe,
        set,
    };
}

function make_target_lang() {
    const inner = writable("");

    function set(value) {
        const uilang = get(ui_lang);
        inner.set(value);
        window.history.pushState(
            null,
            "",
            `/${uilang}/${value}`,
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
        const uilang = get(ui_lang);
        const tlang = get(target_lang);
        window.history.pushState(
            null,
            "",
            `/${uilang}/${tlang}/${value}`
        );
    }

    return {
        subscribe: inner.subscribe,
        set,
    };
}
