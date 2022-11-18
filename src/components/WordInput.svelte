<script>
    /* WordEntry.svelte
         A styled input box for entering search words (but _not_ a "search" box).
    */

    export let value = "";
    export let placeholder = "";

    let input;

    export function focus() {
        input.focus();
    }
</script>

<div>
    <input
        bind:this={input}
        bind:value
        placeholder={placeholder}
    >
</div>

<style>
    div {
        box-sizing: border-box;
        display: inline-flex;
        align-items: center;
        min-height: 3em;
    }
    input {
        font-size: 16px;
        font-family: Roboto, sans-serif;
        border-radius: 12px;
        border: 2px solid #dadada;
        padding: 8px;
        transition:
            width ease-out 0.15s,
            border-radius ease-out 0.15s,
            border-color ease-out 0.15s;
    }
    input:focus {
        border-radius: 6px;
        border: 2px solid #7777ee;
        outline: none;
    }
</style>
