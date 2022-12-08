<script>
    import languageIcon from "../assets/language.svg";
    import { fly } from "svelte/transition";
    import { quintOut } from "svelte/easing";
    import { t } from "svelte-intl-precompile";
    import {
        locale,
        locales,
        locales_in_locale,
        get_langspecific_key,
    } from "../lib/locales.js";

    let open = false;
    const set_locale = loc => () => {
        $locale = loc;
        open = false;
    }

    function onkeydown(ev) {
        if (ev.key !== "Enter") return;
        ev.preventDefault();
        open = !open;
    }

    function on_locale_keydown(ev, loc) {
        if (ev.key !== "Enter") return;
        ev.preventDefault();
        open = false;
        $locale = loc;
    }

    function globalkeydown(ev, loc) {
        if (!open || ev.key !== "Escape") return;
        ev.preventDefault();
        open = false;
    }
</script>

<svelte:window on:keydown={globalkeydown} />

<main>
    <header role="button" tabindex="0" on:keydown={onkeydown} on:click={() => open = !open}>
        <img
            alt="Innholdspråk"
            src={languageIcon}
            height="22"
        />
        <span class="lang-text">
            {locales_in_locale[$locale]}
        </span>
    </header>

    {#if open}
        <div
            in:fly={{ y: -18, duration: 170, easing: quintOut, opacity: 0.2 }}
            out:fly={{ y: -18, duration: 120, easing: quintOut, opacity: 0 }}
            class="fullscreen">
            <h1>{$t("interfacelanguage")}</h1>

            <div class="lang-container">
                {#each locales as loc}
                    <div class="lang" role="button"
                         tabindex="0"
                         on:click={set_locale(loc)}
                         on:keydown={ev => on_locale_keydown(ev, loc)}
                         >{locales_in_locale[loc]}</div>
                {/each}
            </div>
        </div>
    {/if}
</main>

<style>
    main {
        display: flex;
    }
    header {
        display: inline-flex;
        align-items: center;
        cursor: pointer;
    }
    header > span {
        margin-left: 0.4em;
    }
    div.fullscreen {
        color: white;
        background-color: rgba(30, 40, 40, 0.95);
        padding: 16px;
        position: absolute;
        border-radius: 8px;
        left: 34px; top: 28px;
        height: calc(23% - 28px);
    }
    div.fullscreen > h1 {
        margin: 0;
        font-size: 22px;
        padding-left: 18px;
    }
    div.lang-container {
        padding: 0;
        display: inline-flex;
        flex-direction: column;
    }
    div.lang {
        display: inline;
        cursor: pointer;
        margin: 4px 0 0 16px;
        font-size: 1.3em;
        border-bottom: 3px solid transparent;
        transition: border-bottom 0.25s ease-out;
    }
    div.lang:hover {
        border-bottom: 3px solid white;
    }
</style>
