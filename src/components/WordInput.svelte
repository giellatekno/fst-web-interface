<script>
    /* WordEntry.svelte
         A styled input box for entering search words (but _not_ a "search" box).
    */
    import { createEventDispatcher } from "svelte";
    const dispatch = createEventDispatcher();

    export let value = "";
    export let placeholder = "";
    export let debounce = null;

    let input;
    let timer = null;

    export function focus() {
        input.focus();
    }

    function reset() {
        window.clearTimeout(timer);
        timer = null;
        value = "";
        focus();
        dispatch("reset-value");
    }

    function on_debounced() {
        timer = null;
        dispatch("new-value", value);
    }

    function on_input(ev) {
        if (debounce === null) return;
        const value = ev.target.value;

        if (timer === null) {
            if (value !== "") {
                dispatch("new-input-started");
            } else {
                // suddenly after inactivity user
                // pressed ctrl+a backspace
                dispatch("reset-value");
            }
        }

        window.clearTimeout(timer);
        timer = null;

        if (value !== "") {
            timer = window.setTimeout(on_debounced, debounce);
        }
    }
</script>

<div>
    <input
        bind:this={input}
        on:input={on_input}
        bind:value
        placeholder={placeholder}
    >
    <span on:click={reset} class="cross">&#x2718;</span>
</div>

<style>
    div {
        box-sizing: border-box;
        display: inline-flex;
        align-items: center;
        min-height: 3em;
        border-radius: 6px;
        border: 2px solid #9d9db0;
        transition:
            width ease-out 0.15s,
            border-radius ease-out 0.15s,
            border-color ease-out 0.15s;
    }
    div:focus-within {
        border-radius: 12px;
        border: 2px solid #7777ee;
        box-shadow: 0px 2px 8px 0px rgba(200, 200, 255, 0.9);
    }

    input {
        margin-left: 6px;
        font-size: 16px;
        font-family: Roboto, sans-serif;
        border: 0;
        outline: 0;
        padding: 8px;
    }
    input:focus {
        border: 0;
        outline: 0;
    }
    span.cross {
        color: #9d9db0;
        cursor: pointer;
        font-size: 1.5em;
        margin-right: 0.4em;
        transition: color ease-out 0.15s;
    }
    div:focus-within > span.cross {
        color: #f05555;
    }
</style>
