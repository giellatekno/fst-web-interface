import eng from "../../locales/eng.json";
import fin from "../../locales/fin.json";
import nob from "../../locales/nob.json";
import rus from "../../locales/rus.json";
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

addMessages("eng", eng);
addMessages("fin", fin);
addMessages("nob", nob);
addMessages("rus", rus);
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
        window.localStorage.setItem("locale", value);
    }

    return {
        subscribe: inner.subscribe,
        set,
    };
}

function get_initial_locale() {
    const saved_locale = window.localStorage.getItem("locale");
    return saved_locale ?? DEFAULT_LOCALE;
}

export {
    locale,
    locales,
    locales_in_locale,
};
