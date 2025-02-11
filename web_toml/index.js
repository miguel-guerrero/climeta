let argumentCounter = 0;

function addArgument(argument = {}) {
    argumentCounter++;

    const container = document.getElementById('argumentsContainer');
    const argumentDiv = document.createElement('div');
    argumentDiv.className = 'argument';
    argumentDiv.id = `argument_${argumentCounter}`;

    const {
        name = '', short = '', type = 'string',
            default: defaultValue = '', metavar = '', dest = '', multiple = false, required = false, help = '', choices = ''
    } = argument;

    argumentDiv.innerHTML = `
        <button type="button" class="close-btn tooltip" onclick="removeArgument(${argumentCounter})">
            ×
            <span class="tooltip-text">Remove argument</span>
        </button>
        <div class="tooltip">
            <label for="argName_${argumentCounter}">Name:</label>
            <input type="text" id="argName_${argumentCounter}" value="${name}" class="name-option" required 
                   oninput="handleNameChange(${argumentCounter})">
            <span class="tooltip-text">Should be preceded by '--' for a long option. No prefix for positionals.</span>
        </div>
        <div class="tooltip">
            <label for="argShort_${argumentCounter}">Short (optional):</label>
            <input type="text" id="argShort_${argumentCounter}" value="${short}" ${name.startsWith('--') ? '' : 'disabled'} class="short-option">
            <span class="tooltip-text">Optional. Precede by '-'.</span>
        </div>
        <div class="type">
          <label for="argType_${argumentCounter}">Type:</label>
          <select id="argType_${argumentCounter}" onchange="handleTypeChange(${argumentCounter})">
              <option value="string" ${type === 'string' ? 'selected' : ''}>string</option>
              <option value="flag" ${type === 'flag' ? 'selected' : ''}>flag</option>
              <option value="int" ${type === 'int' ? 'selected' : ''}>int</option>
              <option value="float" ${type === 'float' ? 'selected' : ''}>float</option>
          </select>
        </div>
        <div class="tooltip">
            <label for="argDefault_${argumentCounter}">Default (optional):</label>
            <input type="text" id="argDefault_${argumentCounter}" value="${defaultValue}" placeholder="Enter a default value" ${type === 'flag' ? 'placeholder="true/false only"' : ''} class="default-option">
            <span class="tooltip-text">Enter a default value if applicable.</span>
        </div>
        <div class="tooltip">
            <label for="argMetavar_${argumentCounter}">Metavar (optional):</label>
            <input type="text" id="argMetavar_${argumentCounter}" value="${metavar}" class="grey-placeholder metavar-option" placeholder="uses name if empty">
            <span class="tooltip-text">Displayed in help messages.</span>
        </div>
        <div class="tooltip">
            <label for="argDest_${argumentCounter}">Dest (optional):</label>
            <input type="text" id="argDest_${argumentCounter}" value="${dest}" class="grey-placeholder dest-option" placeholder="uses name if empty">
            <span class="tooltip-text">Variable name to store the value.</span>
        </div>
        <div class="tooltip">
            <label for="argHelp_${argumentCounter}">Help:</label>
            <input type="text" class="wider-text" id="argHelp_${argumentCounter}" value="${help}" placeholder="required help" required>
        </div>
        <div class="multiple">
          <label for="argMultiple_${argumentCounter}">Multiple:</label>
          <input type="checkbox" id="argMultiple_${argumentCounter}" ${multiple ? 'checked' : ''}>
        </div>
        <div class="required">
          <label for="argRequired${argumentCounter}">Required:</label>
          <input type="checkbox" id="argRequired_${argumentCounter}" onchange="handleRequiredChange(${argumentCounter})" ${required ? 'checked' : ''}>
        </div>
        <div class="choices-row tooltip">
            <label for="argChoices_${argumentCounter}">Choices (optional):</label>
            <div class="choices-container">
                <select id="argChoices_${argumentCounter}" class="choices-select">
                    ${choices.split(',').filter(c => c.trim()).map(c => 
                        `<option value="${c.trim()}">${c.trim()}</option>`
                    ).join('')}
                </select>
                <input type="text" class="choices-input" id="newChoice_${argumentCounter}" 
                       placeholder="Add new choice">
                <button class="choices-add-btn" onclick="addNewChoice(${argumentCounter})">Add</button>
                <button class="choices-remove-btn" onclick="removeSelectedChoice(${argumentCounter})" 
                        ${!choices ? 'disabled' : ''}>Remove</button>
            </div>
            <span class="tooltip-text">Add or remove valid choices for this argument.</span>
        </div>
    `;

    container.appendChild(argumentDiv);
}

function handleNameChange(id) {
    const nameField = document.getElementById(`argName_${id}`);
    const shortField = document.getElementById(`argShort_${id}`);
    const defaultField = document.getElementById(`argDefault_${id}`);
    const requiredField = document.getElementById(`argRequired_${id}`);

    const name = nameField.value
    if (name.startsWith('-') && !name.startsWith('--') && name != "-") {
        nameField.value = '-' + name
    }

    const isPositional = nameField.value != "" && !nameField.value.startsWith('--');

    // Enable or disable default based on whether it's positional or not
    if (isPositional) {
      defaultField.value = "";
    }
    defaultField.disabled = isPositional;
    requiredField.disabled = isPositional;
    requiredField.checked = isPositional;
    shortField.disabled = isPositional;
}

function handleRequiredChange(id) {
    const required = document.getElementById(`argRequired_${id}`);
    const defaultField = document.getElementById(`argDefault_${id}`);
    if (required.checked) {
      defaultField.disabled = true;
      defaultField.value = "";
    } else {
      defaultField.disabled = false;
    }
}

function handleTypeChange(id) {
    const typeField = document.getElementById(`argType_${id}`);
    const defaultField = document.getElementById(`argDefault_${id}`);
    const required = document.getElementById(`argRequired_${id}`);
    const type = typeField.value;

    if (type === "flag") {
        defaultField.disabled = false;
        defaultField.value = "false";
        defaultField.placeholder = "true/false only";
        required.checked = false;
        required.disabled = true;
    } else {
        required.disabled = false;
        if (type === "int") {
            defaultField.disabled = false;
            defaultField.value = "";
            defaultField.placeholder = "Enter an integer value";
        } else if (type === "float") {
            defaultField.disabled = false;
            defaultField.value = "";
            defaultField.placeholder = "Enter a float value";
        } else {
            defaultField.disabled = false;
            defaultField.value = "";
            defaultField.placeholder = "Enter a default value";
        }
    }
}

function removeArgument(id) {
    const argumentDiv = document.getElementById(`argument_${id}`);
    argumentDiv.remove();
}

document.getElementById('argumentForm').addEventListener('submit', function(e) {
    e.preventDefault();
    generateTOML();
});

function generateTOML() {
    const programName = document.getElementById('programName').value;
    const programDescription = document.getElementById('programDescription').value;
    const programEpilog = document.getElementById('programEpilog').value;

    let hasError = false;
    let tomlContent = `[program]\nname = "${programName}"\ndescription = "${programDescription}"\n`;
    if (programEpilog) {
        tomlContent += `epilog = "${programEpilog}"\n`;
    }
    tomlContent += `\n`;

    const argumentsContainer = document.getElementById('argumentsContainer');
    const argumentDivs = argumentsContainer.querySelectorAll('.argument');
    argumentDivs.forEach(div => {
        const id = div.id.split('_')[1];
        const nameField = document.getElementById(`argName_${id}`);
        const typeField = document.getElementById(`argType_${id}`);
        const helpField = document.getElementById(`argHelp_${id}`);
        const defaultField = document.getElementById(`argDefault_${id}`);

        const name = nameField.value;
        const type = typeField.value;
        const help = helpField.value;
        const short = document.getElementById(`argShort_${id}`).value;
        const defaultValue = defaultField.value;
        const metavar = document.getElementById(`argMetavar_${id}`).value;
        const dest = document.getElementById(`argDest_${id}`).value;
        const multiple = document.getElementById(`argMultiple_${id}`).checked;
        const required = document.getElementById(`argRequired_${id}`).checked;
        const choicesSelect = document.getElementById(`argChoices_${id}`);
        const choices = Array.from(choicesSelect.options).map(opt => opt.value).join(',');

        // Validate mandatory fields
        if (!name || !type || !help) {
            hasError = true;
            if (!name) nameField.classList.add('error');
            if (!type) typeField.classList.add('error');
            if (!help) helpField.classList.add('error');
            return;
        } else {
            nameField.classList.remove('error');
            typeField.classList.remove('error');
            helpField.classList.remove('error');
        }

        // Validate type-specific defaults
        if (type === "flag" && defaultValue !== "true" && defaultValue !== "false") {
            hasError = true;
            defaultField.classList.add('error');
            return;
        }
        if (type === "flag" && !name.startsWith('--')) {
            // flags must be -- options
            hasError = true;
            defaultField.classList.add('error');
            return;
        }
        if (type === "int" && defaultValue && isNaN(parseInt(defaultValue))) {
            hasError = true;
            defaultField.classList.add('error');
            return;
        } 
        if (type === "float" && defaultValue && isNaN(parseFloat(defaultValue))) {
            hasError = true;
            defaultField.classList.add('error');
            return;
        }
        defaultField.classList.remove('error');

        tomlContent += `[[arguments]]\nname = "${name}"\n`;
        if (short) {
            tomlContent += `short = "${short}"\n`;
        }
        tomlContent += `type = "${type}"\n`;
        if (defaultValue) {
            tomlContent += `default = "${defaultValue}"\n`;
        }
        if (metavar) {
            tomlContent += `metavar = "${metavar}"\n`;
        }
        if (dest) {
            tomlContent += `dest = "${dest}"\n`;
        }
        if (multiple) {
            tomlContent += `multiple = "true"\n`;
        }
        if (required) {
            tomlContent += `required = "true"\n`;
        }
        if (choices) {
            tomlContent += `choices = "${choices}"\n`;
        }
        tomlContent += `help = "${help}"\n\n`;
    });

    if (hasError) {
        alert("Please fix the highlighted errors.");
        return;
    }

    // Create a download link for the generated TOML file
    const blob = new Blob([tomlContent], {
        type: 'text/plain'
    });
    const link = document.getElementById('downloadLink');
    link.href = URL.createObjectURL(blob);
    link.download = 'cli_config.toml';
    link.textContent = 'Download TOML';
    link.classList.remove('hidden');
}

function resetTOMLFileName() {
    // Clear the file input’s value to allow re-selection of the same file
    const fileInput = document.getElementById('importTOML');
    fileInput.value = '';
}

function importTOMLFile() {
    const fileInput = document.getElementById('importTOML');
    const file = fileInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const content = e.target.result;
            parseTOML(content);
        };
        reader.readAsText(file);
    } else {
        alert("Please select a valid .toml file.");
    }
}

function parseTOML(content) {
    const lines = content.split('\n');
    let currentArg = null;
    let programInfo = {};
    let argumentsList = [];

    lines.forEach(line => {
        line = line.trim();
        if (line.startsWith('[program]')) {
            currentArg = null;
        } else if (line.startsWith('[[arguments]]')) {
            if (currentArg) {
                argumentsList.push(currentArg);
            }
            currentArg = {};
        } else if (line) {
            const [key, value] = line.split('=').map(s => s.trim().replace(/^"|"$/g, ''));
            if (currentArg) {
                currentArg[key] = value;
            } else {
                programInfo[key] = value;
            }
        }
    });

    if (currentArg) {
        argumentsList.push(currentArg);
    }

    document.getElementById('programName').value = programInfo.name || '';
    document.getElementById('programDescription').value = programInfo.description || '';
    document.getElementById('programEpilog').value = programInfo.epilog || '';

    document.getElementById('argumentsContainer').innerHTML = '';

    argumentsList.forEach(arg => addArgument(arg));
}

function addNewChoice(id) {
    const dropdown = document.getElementById(`argChoices_${id}`);
    const newChoiceInput = document.getElementById(`newChoice_${id}`);
    const newChoice = newChoiceInput.value.trim();
    const removeBtn = dropdown.parentElement.querySelector('.choices-remove-btn');

    if (newChoice) {
        // Check if the choice already exists
        const existingOptions = Array.from(dropdown.options).map(option => option.value);
        if (!existingOptions.includes(newChoice)) {
            const newOption = document.createElement('option');
            newOption.value = newChoice;
            newOption.textContent = newChoice;
            dropdown.appendChild(newOption);
            
            newChoiceInput.value = '';
            removeBtn.disabled = false;

            if (dropdown.options.length > 0) {
                dropdown.selectedIndex = dropdown.options.length - 1;
            }
        } else {
            alert('This choice already exists.');
        }
    }
}

function removeSelectedChoice(id) {
    const dropdown = document.getElementById(`argChoices_${id}`);
    const removeBtn = dropdown.parentElement.querySelector('.choices-remove-btn');
    const currentSelectedIndex = dropdown.selectedIndex;
    
    if (currentSelectedIndex !== -1) {
        dropdown.remove(currentSelectedIndex);
        
        if (dropdown.options.length > 0) {
            if (currentSelectedIndex < dropdown.options.length) {
                dropdown.selectedIndex = currentSelectedIndex;
            } else {
                dropdown.selectedIndex = dropdown.options.length - 1;
            }
        }
        
        if (dropdown.options.length === 0) {
            removeBtn.disabled = true;
        }
    }
}
