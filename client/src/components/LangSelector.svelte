<script>
    import { t } from "svelte-intl-precompile";
    import { locale } from "../lib/locales.js";
    import {
        language_names,
    } from "../lib/langs.js";
    import { lang } from "../lib/stores.js";

    $: current_lang = language_names[$locale][$lang];
</script>

<main>
    {#if $lang}
        <span class="separator">&#xB7;</span>
        {$t("nowexploring")} {current_lang}&nbsp;
        <a href="/">
            {$t("exploreanotherlang")}
        </a>
    {/if}
</main>

<style>
    main {
        display: inline-flex;
        align-items: center;
    }

    span.separator {
        margin-left: 6px;
        margin-right: 6px;
    }
</style>
