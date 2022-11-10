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
export const selected_tool = writable("");

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


// factory function for making the
// writable store for our target_lang store
// The reason why we do this, is so that
// we can do custom logic when someone
// set the store
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

function make_ui_lang() {
    const inner = writable("");

    function set(value) {
        inner.set(value);
        const uilang = get(ui_lang);
        const tlang = get(target_lang);
        console.log("replacestate now");
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
