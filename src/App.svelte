<script>
  import { t, locale } from "svelte-intl-precompile";
  import { ui_langs } from "./lib/config.js";
  import UILangSelector from "./UILangSelector.svelte";
  import Index from "./Index.svelte";
  import Tools from "./Tools.svelte";

  import {
      ui_lang,
      target_lang,
      selected_tool,
  } from "./lib/stores.js";

  // React to any changes in ui_lang,
  // target_lang, or tool, and update the
  // currenly showing component
  $: current_component = determine_component(
      $ui_lang,
      $target_lang,
      $selected_tool,
  );

  function determine_component(
      ui_lang,
      target_lang,
      tool,
  ) {
      const m = "App.svelte::determine_component()";
      if (!ui_lang) ui_lang = "sme";
      if (!target_lang) {
          console.debug(m + ": show Index");
          return Index;
      } else {
          console.debug(m + ": show Tools");
          return Tools;
      }
  }

  let selecting_language = false;
  let more_languages = false;
  function select_langauge() {
    selecting_language = !selecting_language;
  }

  function show_more_languages() {
    num_langs_shown = langs.length;
  }
</script>

<main>
    <UILangSelector />

    <svelte:component
        this={current_component}
    />
</main>


<style>
/*
  .logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }
  .logo.svelte:hover {
    filter: drop-shadow(0 0 2em #ff3e00aa);
  }
  .read-the-docs {
    color: #888;
  }
  */

  span.link {
    cursor: pointer;
    text-decoration: underline;
    color: blue;
  }
  div.big {
    margin-left: 18px;
    font-size: 18px;
    }
    div.small {
        margin-left: 18px;
    font-size: 14px;
    }
</style>
