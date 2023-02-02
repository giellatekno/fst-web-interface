<script>
    import { onMount } from "svelte";
    import example_img from "../assets/language.svg";
    import spellcheck_img from "../assets/spellcheck.svg";
    import hyphenation_img from "../assets/hyphenation.svg";
    import num_img from "../assets/num.svg";
    import ipa_img from "../assets/ipa.svg";
    import { t } from "svelte-intl-precompile";
    import { locale } from "../lib/locales.js";
    import { capabilities_for_lang } from "../lib/api.js";
    import {
        only_on_enter,
        fmt_date_ago_localized,
    } from "../lib/utils";
    import {
        lang,
        lang_in_locale,
    } from "../lib/stores.js";
    import {
        language_names,
        tools_for
    } from "../lib/langs.js";

    function get_copyright($t, $lang) {
        const specific_key = `copyright.lang.${$lang}`;
        const specific_value = $t(specific_key);
        if (specific_value !== specific_key) {
            return specific_value;
        } else {
            const generic_key = `copyright`;
            const generic_value = $t(generic_key);
            if (generic_value !== generic_key) {
                return generic_value;
            } else {
                // ??
                return "";
            }
        }
    }

    const IMAGES = {
        spellcheck: spellcheck_img,
        hyphenation: hyphenation_img,
        num: num_img,
        transcription: ipa_img,
    }

    let repo_info = null;
    let show_date_relative = false;
    let tools_available = [];

    onMount(async () => {
        await get_repo_info($lang);
        tools_available = repo_info.tools;
    });

    $: get_repo_info($lang);
    $: repo_date = fmt_date_localized($locale, repo_info);
    $: repo_date_ago = fmt_date_ago_localized(repo_info?.date, $locale);

    $: copyright = get_copyright($t, $lang);
    $: tools = tools_for[$lang];

    const FMT_DATE_OPTS = { day: "numeric", month: "short", year: "numeric" };

    function fmt_date_localized(locale, repo_info) {
        if (!repo_info || repo_info == "no api") return null;
        const date = repo_info.date;
        return date.toLocaleDateString(locale, FMT_DATE_OPTS);
    }

    async function get_repo_info(lang) {
        if (!lang) throw Error();
        const obj = await capabilities_for_lang(lang);
        if (!obj || !obj.commit) {
            console.warn("error getting repo info");
            repo_info = "no api";
        } else {
            obj.date = new Date(obj.date);
            repo_info = obj;
        }
    }
</script>

<main>
    <h2>{$t("lt")} {$t(`lname.lang.${$lang}`)}</h2>

    <div class="tools-wrapper">
        {#each tools as tool}
            <a href="/{$lang}/{tool}" class="tool" class:grayed={!tools_available.includes(tool)}>
                <img src={IMAGES[tool] || example_img} alt="">
                <span class="title">{$t(tool)}</span>
                <span class="desc">
                    {@html $t(tool + ".description")}
                </span>
            </a>
        {/each}
    </div>

    <p>
        Andre ressurser for {$lang_in_locale}
    </p>

    <!-- TODO: current page link -->
    <a href="/">Direktelenke for denne siden</a>

    {#if repo_info}
        <div style="margin-top: 3em;">
            <p class="langmodel-info" class:no-api={repo_info === "no api"}>
                {#if repo_info === "no api"}
                    Error: no API available! (tools will not work at all)
                {:else}
                    {$t("langmodellastupdated")}
                    <span role="button" class="date"
                        on:click={() => show_date_relative = !show_date_relative}
                        on:keydown={only_on_enter(() => show_date_relative = !show_date_relative)}
                    >
                        {show_date_relative ? repo_date_ago : repo_date}
                    </span>&mdash;&nbsp;<code>commit {repo_info.commit},
                        <a rel="external" href="https://github.com/giellalt/lang-{$lang}"
                        >github.com/giellalt/lang-{$lang}</a></code>
                {/if}
            </p>
        </div>
    {/if}

    <p>{@html copyright}</p>
</main>


<style>
    main {
        margin-left: 34px;
    }

    span.date {
        cursor: pointer;
        border-bottom: 1px dashed black;
    }

    div.tools-wrapper {
        display: grid;
        grid-template-columns: repeat(2, max-content);
        grid-gap: 17px;
        /*width: calc(100vw - 68px);*/
    }

    @media screen and (max-width: 768px) {
        div.tools-wrapper {
            grid-template-columns: 1fr;
        }
    }

    a.tool { 
        display: grid;
        color: black;
        text-decoration: none;
        grid-template-areas:
            'img img title title title'
            'img img desc desc desc';
        grid-template-columns: 35px 35px repeat(3, max-content);
        background-color: #f2ecb7;
        border: 1px solid #d5b867;
        border-radius: 4px;
        padding: 4px 12px;
        box-shadow: 2px 2px 4px 0px rgba(121, 121, 89, 0.44);
        transition:
            background-color ease-out 0.25s;
    }

    a.tool.grayed {
        filter: grayscale(1.0) blur(0.5px);
        color: #757272;
        box-shadow: 2px 2px 4px 0px rgba(0, 0, 0, 0.44);
    }

    @media screen and (max-width: 768px) {
        a.tool {
        }
    }

    a.tool:hover {
        background-color: #ece268;
    }

    a.tool > img {
        align-self: center;
        grid-area: img;
        height: 68px;
        width: 68px;
    }

    a.tool > span.title {
        margin-left: 10px;
        justify-self: start;
        align-self: end;
        grid-area: title;
        font-size: 1.6em;
        font-weight: 500;
        font-variant: small-caps;
        margin-bottom: 6px;
    }

    a.tool > span.desc {
        margin-left: 12px;
        justify-self: start;
        align-self: start;
        grid-area: desc;
        font-style: italic;
        font-size: 1.05em;
    }

    p.langmodel-info {
        display: inline;
        font-size: 0.85em;
        padding: 8px 10px;
        border: 2px solid #d9d914;
        background-color: #f4f49c;
    }

    p.langmodel-info.no-api {
        background: #ff5656;
        border: 2px solid #e31919;
    }

    p.langmodel-info,
    p.langmodel-info a,
    p.langmodel-info code {
        color: #111;
    }
</style>
