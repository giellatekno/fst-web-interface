export function only_on_enter(fn) {
    return function (ev) {
        if (ev.key !== "Enter") return;
        fn();
    }
}

export function *enumerate(list, start = 0) {
    for (let i = start; i < list.length; i++) {
        yield [i, list[i]];
    }
}

export function len(obj) {
    const length = obj.length;
    if (length !== undefined) return length;

    if (is_pojo(obj)) {
        return Object.keys(obj).length;
    }

    if (obj instanceof Set || obj instanceof Map) {
        return obj.size;
    }

    throw new TypeError(`len(): object of type '${_typeof(obj)}' has no length`);
}

export function _typeof(obj) {
    if (obj === null) return "null";
    const t = typeof obj;
    switch (t) {
        case "undefined":
        case "number":
        case "string":
        case "symbol":
            return t;
    }
    return obj.constructor.name;
}

export function is_primitive(obj) {
    if (obj === null || obj === undefined) return true;
    switch (obj.constructor) {
        case Number:
        case BigInt:
        case String:
        case Symbol:
            return true;
        default:
            return false;
    }
}

// checks if two objects are equal, deeply
// useful for testing
export function is_equal(a, b) {
    if (Object.is(a, b)) return true;

    if (Array.isArray(a) && Array.isArray(b)) {
        if (a.length !== b.length) return false;

        for (const [x, y] of zip(a, b)) {
            if (!is_equal(x, y)) return false;
        }

        return true;
    }

    if (!(is_primitive(a) && is_primitive(b)) &&
         (a.constructor === b.constructor)) {
        for (const key in a) {
            if (!(key in b)) return false;
            if (!is_equal(a[key], b[key])) return false;
        }

        return true;
    }

    return false;
}

/*
(function test_is_equal() {
    console.assert(is_equal(null, null));
    console.assert(is_equal(undefined, undefined));
    console.assert(is_equal(true, true));
    console.assert(is_equal(false, false));
    console.assert(is_equal(1, 1));
    console.assert(is_equal(92.4, 92.4));
    console.assert(is_equal("xYz", "xYz"));
    console.assert(
        is_equal(["a", 1, false], ["a", 1, false]),
        'is_equal(["a", 1, false], ["a", 1, false])'
    );
    console.assert(
        !is_equal(["a", 1, false], ["a", 2, false]),
        '!is_equal(["a", 1, false], ["a", 2, false])'
    );
    console.assert(is_equal(
        {a: [1, 2, 3], b: null, c: [{x: 2}, {y: 3}, false]},
        {a: [1, 2, 3], b: null, c: [{x: 2}, {y: 3}, false]},
    ));
    console.log("is_equal() seems to work");
})();
//*/



/* strip()
 *   argument strip_characters: iterable of characters (e.g. a str)
 *     (which characters to strip)
 * returns
 *   a function that takes a string,
 *   and it strips away the 'strip_characters' from the beginning and the end
 *
 * This function uses "currying".
 * Example use:
 *   [" abc ", "xx  ", "  yy" ].map(strip()); // ["abc", "xx", "yy"]
 *   or
 *   const strip_whitespace = strip(" \t\n");
 *   [" abc ", "xx  ", "  yy" ].map(strip_whitespace); // ["abc", "xx", "yy"]
 */
export function strip({ characters = " \t\n", from_beginning = true, from_end = true }) {
    try {
        characters = new Set(characters);
    } catch (e) {
        if (e instanceof TypeError) {
            throw new TypeError("strip(): 'characters' must be an iterable of strings of length 1", { cause: e });
        } else {
            throw e;
        }
    }

    for (const character of characters) {
        if (typeof character !== "string") {
            throw new TypeError("strip(): 'characters' must be an iterable of strings of length 1");
        }

        if (character.length !== 1) {
            throw new TypeError("strip(): 'characters' must be an iterable of strings of length 1");
        }
    }

    return function (str) {
        if (typeof str !== "string") {
            throw new TypeError("strip(): input must be a string");
        }

        let start = -1;
        let end = str.length;

        while (from_beginning && characters.has(str[++start])) ;
        while (from_end && characters.has(str[--end])) ;

        return str.slice(start, end + 1);
    }
}

export const strip_whitespace = strip({ characters: " \t\n" });

export function *range(...args) {
    let start = 0, stop = null, step = 1;
    switch (args.length) {
        case 1: stop = args[0]; break;
        case 2: start = args[0]; stop = args[1]; break;
        case 3: start = args[0]; stop = args[1]; step = args[2]; break;
    }

    const going_up = step > 0;
    let i = start;
    if (going_up) {
        for (; i < stop; i += step) yield i;
    } else {
        for (; i > stop; i += step) yield i;
    }
}

export function any(iterable) {
    for (let element of iterable) {
        if (element) return true;
    }

    return false;
}

export function all(iterable) {
    for (let element of iterable) {
        if (element) return false;
    }

    return true;
}

// pad out the string `str` to length `size`,
// padding by spaces on each side
export function pad_center(str, size) {
    if (typeof size !== "number") {
        throw new TypeError("pad_center(): argument 'size' must be a number");
    }

    const to_pad = size - len(str);
    if (to_pad <= 0) {
        return str;
    }

    let pad_left, pad_right;
    if (to_pad % 2 === 0) {
        pad_left = pad_right = to_pad / 2;
    } else {
        pad_left = to_pad / 2;
        pad_right = to_pad / 2 + 1;
    }

    pad_left = " ".repeat(pad_left);
    pad_right = " ".repeat(pad_right);
    const result = pad_left + str + pad_right;
    console.assert(result.length === size, `${result.length} != ${size}`);
    return result;
}

export function _iter(obj) {
    if (typeof obj === "undefined") {
        throw new TypeError("iter(): undefined is not iterable");
    }
    if (obj === null) {
        throw new TypeError("iter(): null is not iterable");
    }
    if (typeof obj === "boolean") {
        throw new TypeError("iter(): boolean is not iterable");
    }

    if (obj && typeof obj.next === "function") {
        // probably not a good enough check, but whatevs
        return obj;
    }

    const it = obj[Symbol.iterator];
    if (typeof it === "function") {
        return it.call(obj);
    }

    if (is_pojo(obj)) {
        return object_iter(obj);
    }

    throw new TypeError("iter(): don't know how to make an iterator out of that");
}

function *object_iter(obj) {
    for (let key in obj) {
        if (Object.hasOwn(obj, key)) {
            yield [key, obj[key]];
        }
    }
}

export function *zip(...iterables) {
    const iterators = iterables.map(_iter);
    outer: while (true) {
        const next_result = [];
        for (const it of iterators) {
            const next_it_result = it.next();
            if (next_it_result.done) break outer;
            next_result.push(next_it_result.value);
        }
        yield next_result;
    }
}

/*
    deep_len(arr)
    total length of array `arr`, including length of subarrays, e.g.
    tot_len([1, 2, 3]) == 3,
    tot_len([1, 2, [3, 4]]) == 4
*/
export const deep_len = arr => !Array.isArray(arr) ? 1 : arr.map(deep_len).reduce((prev, cur) => prev + cur);
export const is_pojo = obj => !!obj && obj.constructor === Object;

// https://blog.webdevsimplified.com/2020-07/relative-time-format/
const DIVISIONS = [
    { amount: 60, name: 'seconds' },
    { amount: 60, name: 'minutes' },
    { amount: 24, name: 'hours' },
    { amount: 7, name: 'days' },
    { amount: 4.34524, name: 'weeks' },
    { amount: 12, name: 'months' },
    { amount: Number.POSITIVE_INFINITY, name: 'years' },
];

const RELTIME_FMT_OPTS = { };
export function fmt_date_ago_localized(date, locale) {
    if (!date) return null;
    let diff_sec = (date - Date.now()) / 1000;

    const formatter = new Intl.RelativeTimeFormat(locale, RELTIME_FMT_OPTS);
    for (let i = 0; i <= DIVISIONS.length; i++) {
        const division = DIVISIONS[i]
        if (Math.abs(diff_sec) < division.amount) {
            return formatter.format(Math.round(diff_sec), division.name)
        }
        diff_sec /= division.amount
    }

    // the loop with the if check should always hit, so we return early.
    // if that doesn't happen, something is very wrong
    throw new Error("unreachable?");
}
