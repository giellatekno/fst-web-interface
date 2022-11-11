<script>
  import { locale, locales } from "./lib/locales.js";
  import LocaleSelector from "./components/LocaleSelector.svelte";
  import LangSelector from "./components/LangSelector.svelte";
  import Index from "./routes/Index.svelte";
  import Tools from "./routes/Tools.svelte";
  import AnalyzeWord from "./routes/AnalyzeWord.svelte";

  import { lang, tool } from "./lib/stores.js";

  // React to any changes in locale, lang or tool,
  // and update the currenly showing component
  $: current_component = determine_component(
      $locale,
      $lang,
      $tool,
  );

  function determine_component(locale, lang, tool) {
      if (!locale) locale = "sme";
      if (!lang) {
          return Index;
      } else {
          if (!tool) {
              return Tools;
          } else {
              return AnalyzeWord;
          }
      }
  }
</script>

<main>
    <header>
        <LocaleSelector />
        <span class="separator">&#xB7;</span>
        <LangSelector />
    </header>

    <div>
        <svelte:component
            this={current_component}
        />
    </div>
</main>


<style>
    header {
        display: flex;
        align-items: center;
        margin-top: 6px;
        margin-left: 6px;
    }
    header > span.separator {
        margin-left: 6px;
        margin-right: 6px;
    }

    div {
        margin-left: 34px;
    }
</style>
