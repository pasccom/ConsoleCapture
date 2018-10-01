function capture(objName) {
    var captured = [];

    var obj = window[objName];
    var newObj = {
        get: function() {
            return cloneInto(captured, window);
        },
        original: {},
    };

    Object.keys(obj).forEach((key) => {
        newObj[key] = function() {
            obj[key](... arguments);

            var cap = {
                level: key,
                time: Date.now(),
                arguments: Array.prototype.slice.call(arguments),
            };

            var stack = (new Error()).stack.split('\n');
            var stackLineFields = (/^([^@]*)@(.*):(\d+):(\d+)$/).exec(stack[1]);

            if (stackLineFields !== null) {
                cap.function = stackLineFields[1];
                cap.fileName = stackLineFields[2];
                cap.lineNumber = stackLineFields[3];
                cap.columnNumber = stackLineFields[4];
            }

            captured.push(cap);
        };
        newObj.original[key] = function() {
            obj[key](... arguments);
        };
    });

    window.wrappedJSObject[objName] = cloneInto(newObj, window, {cloneFunctions: true});
}

capture('console');
