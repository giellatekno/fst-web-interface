<script>
    import languageIcon from "./assets/language.svg";
    import { fly } from "svelte/transition";
    import { quintOut } from "svelte/easing";
    import { locale } from "svelte-intl-precompile";
    import {
        ui_langs,
        ui_langs_long,
    } from "./lib/config.js";
    import { ui_lang } from "./lib/stores";

    let open = false;
    const toggle = () => open = !open;
    const set_lang = lang => () => {
        $locale = lang;
        console.log("change $ui_lang now");
        $ui_lang = lang;
        open = false;
    }
</script>

<div>
    <header>
    <img
        alt="Innholdspråk"
        on:click={toggle}
        src={languageIcon}
        height="22"
    />
    <span class="lang-text">
        {ui_langs_long[$locale]}
    </span>
    </header>

    {#if open}
        <div
            in:fly={{ y: -18, duration: 170, easing: quintOut, opacity: 0.2 }}
            out:fly={{ y: -18, duration: 120, easing: quintOut, opacity: 0 }}
            class="fullscreen">
            <h1>Velg grensesnittspråk...</h1>

            {#each ui_langs as lang}
                <div class="lang" on:click={set_lang(lang)}>{lang}</div>
            {/each}
        </div>
    {/if}
</div>

<style>
    header {
        margin-top: 6px;
        margin-left: 6px;
        display: flex;
        align-items: center;
    }
    header > span {
        margin-left: 0.4em;
    }
    div.fullscreen {
        padding: 26px;
        position: absolute;
        background-color: rgba(240, 245, 240, 0.95);
        left: 0; top: 28px;
        height: calc(40% - 28px);
        width: 100%;
    }
    div.lang {
        cursor: pointer;
        margin: 18px;
        font-size: 1.4em;
    }
</style>
