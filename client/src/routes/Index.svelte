<script>
    import { onMount } from "svelte";
    import { t } from "svelte-intl-precompile";
    import { locale } from "../lib/locales.js";
    import { only_on_enter } from "../lib/utils.js";
    import {
        langs,
        language_names,
        sami_langs,
        nonsamiuralic_langs,
        other_langs,
    } from "../lib/langs.js";
    import { lang } from "../lib/stores.js";
    import Search from "../components/Search.svelte";
    import {
        capabilities,
    } from "../lib/api.js";

    let search = "";
    let show_sami = false;
    let show_uralic = false;
    let show_others = false;
    let langs_in_api = [];

    $: visible_langs = filter_langs(search, show_sami, show_uralic, show_others);

    onMount(async () => {
        const cap = await capabilities();
        langs_in_api = Object.keys(cap);
    });

    function filter_langs(search, show_sami, show_uralic, show_others) {
        const any_filters_on = show_sami || show_uralic || show_others;
        let rootset = langs;
        if (any_filters_on) {
            rootset = [];
            if (show_sami) rootset.push(...sami_langs);
            if (show_uralic) rootset.push(...nonsamiuralic_langs);
            if (show_others) rootset.push(...other_langs);
        }

        if (search === "") {
            return rootset;
        } else {
            // bad code quality / hard to read ahead:
            // What: In the set of languages to be searched from, include
            //   all language names in the locale, so that you can search for "norsk",
            //   and it will return the codes for "norsk bokmål" and "norsk nynorsk".
            // How: By first grabbing all locale names, not including the ones
            //   that are filtered away. this gives an object of  locale_name => lang code
            //   add to that also all lang_codes, so that the object also includes
            //     lang_code => lang_code.
            //   Take the keys of this object, and do the search filtering on it.
            //   Then, those who matched will have to be "flipped back", i.e. to go from
            //   an object of { code or locale => code } and back to just the code.
            //   It is necessary because the loop that shows search results expects
            //   only lang codes.

            const flipped = {};
            for (const [abbr, langinlocale] of Object.entries(language_names[$locale])) {
                if (!rootset.includes(abbr)) continue;
                flipped[langinlocale] = abbr;
            }
            for (const abbr of rootset) {
                flipped[abbr] = abbr;
            }

            const search_set = Object.keys(flipped);
            const search_hits = search_set.filter(key =>
                search.includes(key) || key.includes(search));

            const flipped_back = search_hits.map(sh => flipped[sh]);
            // this flipped back can have a hit on both "no" in the code, and in the
            // name of the langauge, so we make unique by converting to a set and back
            return [...new Set(flipped_back)];
        }
    }

    let langs_container_el;
    function onenter() {
        if (visible_langs.length === 1) {
            const lang = visible_langs[0];

            // this is this "hacky" because...
            const link_el = langs_container_el.querySelector("a");
            link_el.click();

            // ...this does a full page reload
            //window.location = `/${lang}`;

            // ...and this doesn't trigger our logic
            //window.history.pushState(null, "", `/${lang}`);
        }
    }
</script>

<main>
    <h1>{$t("languagetools")}</h1>
    <div>
        <h2>{$t("index.showtoolsfordotdotdot")}</h2>

        <Search on:enter={onenter} bind:value={search} />

        <div class="filters">
            <span class="header">{$t("filters")}:</span>

            <span
                class="label"
                role="button"
                tabindex="0"
                class:on={show_sami}
                on:click={() => show_sami = !show_sami}
                on:keydown={only_on_enter(() => show_sami = !show_sami)}
            >
                <label for="sami">{$t("samilanguages")}</label>
                <input name="sami" type="radio" checked={show_sami} />
            </span>
            <span
                class="label"
                role="button"
                tabindex="0"
                class:on={show_uralic}
                on:click={() => show_uralic = !show_uralic}
                on:keydown={only_on_enter(() => show_uralic = !show_uralic)}
            >
                <label for="uralicnonsami">{$t("nonsamiuralic")}</label>
                <input name="uralicnonsami" type="radio" checked={show_uralic} />
            </span>
            <span
                class="label"
                role="button"
                tabindex="0"
                class:on={show_others}
                on:click={() => show_others = !show_others}
                on:keydown={only_on_enter(() => show_others = !show_others)}
            >
                <label for="others">{$t("otherlanguages")}</label>
                <input name="others" type="radio" checked={show_others} />
            </span>
        </div>

        <div class="langs" bind:this={langs_container_el}>
            {#each visible_langs as lng}
                <span class="language" class:grayed={!langs_in_api.includes(lng)}>
                    <a href="/{lng}">
                        {$t(`lname.lang.${lng}`)}
                        <!--{language_names[$locale][lng]}-->
                    </a>
                </span>
            {:else}
                [l6e] Ingen treff på søkeordet...
            {/each}
        </div>
    </div>
</main>

<style>
    main {
        margin-left: 34px;
    }

    main > h1 {
        margin-top: 0.2em;
    }

    a {
        color: blue;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    div.langs {
        margin-top: 1em;
        display: grid;
        width: 800px;
        grid-template-columns: 1fr 1fr 1fr 1fr;
    }

    div.langs > span.language.grayed > a {
        color: gray;
    }

    div.filters {
        display: flex;
        font-variant: small-caps;
    }

    div.filters > span.header {
        user-select: none;
        padding: 2px 0px;
        border-radius: 5px;
        color: #000;
        font-weight: bold;
    }

    span.label {
        margin-left: 16px;
        padding: 2px 8px;
        border-radius: 5px;
        background-color: #d9d9d9;
        color: #292929;
        font-weight: bold;
        transition:
            background-color 0.2s ease-out,
            color 0.2s ease-out;
    }

    span.label:hover,
    span.label > label:hover {
        cursor: pointer;
    }

    span.label.on {
        background-color: #4651ea;
        color: white;
    }

    span.label > input {
        appearance: none;
        display: none;
    }

    span.label > label {
        user-select: none;
    }

    h2 {
        display: inline;
        font-size: 1.4em;
        font-weight: normal;
    }

    span.language {
        font-size: 20px;
        padding: 6px;
    }
</style>
