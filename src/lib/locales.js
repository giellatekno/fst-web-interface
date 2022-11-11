import nob from "../../locales/nob.json";
import eng from "../../locales/eng.json";
import sme from "../../locales/sme.json";

import {
    addMessages,
    init,
    locale as precompile_locale,
} from 'svelte-intl-precompile';

const DEFAULT_LOCALE = "sme";
const locale = wrap_precompile_locale();
const locales = [
   "nob", "eng", "fin", "rus", "sme"
];

addMessages("nob", nob);
addMessages("eng", eng);
addMessages("sme", sme);

init({
    fallbackLocale: DEFAULT_LOCALE,
    initialLocale: get_initial_locale(),
});

const locales_in_locale = {
    nob: "Norsk Bokmål",
    eng: "English",
    sme: "Davvisámegillii",
    fin: "Suomeksi",
    rus: "Русский"
};

function wrap_precompile_locale() {
    const inner = precompile_locale;

    function set(value) {
        inner.set(value);

        console.debug("todo: locale store changed, update url accordingly");
    }

    return {
        subscribe: inner.subscribe,
        set,
    };
}

function get_initial_locale() {
    const path = window.location.pathname;
    let initial = DEFAULT_LOCALE;
    if (path.length > 1) {
        const from_url = path.slice(1, 4);
        if (locales.includes(from_url)) {
            initial = from_url;
        } else {
            // silently ignore and choose default
        }
    }
    return initial;
}

export {
    locale,
    locales,
    locales_in_locale,
};
