const $select = $("#select-students"); // Fixed ID
const $selectedItems = $("#selected-items");

const allOptions = [];
$select.find("option").each(function () {
  const val = $(this).val();
  if (val) {
    allOptions.push({ value: val, text: $(this).text() });
  }
});

let selectedStudents = [];

function renderSelected() {
  $selectedItems.empty();
  selectedStudents.forEach((student) => {
    const $tag = $(`
      <div class="bg-primary text-white text-sm px-3 py-1 rounded flex items-center gap-2">
        <span>${student.text}</span>
        <button type="button" class="remove-tag focus:outline-none" title="Remove">&times;</button>
      </div>
    `);
    $tag.find(".remove-tag").click(function () {
      selectedStudents = selectedStudents.filter(
        (s) => s.value !== student.value
      );
      updateSelectOptions();
      renderSelected();
    });
    $selectedItems.append($tag);
  });
}

function updateSelectOptions() {
  allOptions.forEach((opt) => {
    const alreadySelected = selectedStudents.some((s) => s.value === opt.value);
    if (!alreadySelected) {
      $select.append(`<option value="${opt.value}">${opt.text}</option>`);
    }
  });
}

$select.change(function () {
  const val = $(this).val();
  const text = $(this).find("option:selected").text();
  if (val && !selectedStudents.some((s) => s.value === val)) {
    selectedStudents.push({ value: val, text });
    updateSelectOptions();
    renderSelected();
  }
});

updateSelectOptions();
renderSelected();
