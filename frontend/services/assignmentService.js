class AssignmentService {
  async handleAddAssignment(obj) {
    try {
      const { data } = await api.post("/assignment/add", obj);
      return data.message;
    } catch (error) {
      console.error("Error:", error.response?.data || error.message);
      throw error;
    }
  }

  async getAssignments(user_id) {
    try {
      const { data } = await api.get(`/assignment/by?created_by=${user_id}`);
      return data.payload;
    } catch (error) {
      console.error("Error:", error.response?.data || error.message);
      throw error;
    }
  }

  async deleteAssignments(assignment_id) {
    try {
      const { data } = await api.delete(`/assignment/remove/${assignment_id}`);
      return data.message;
    } catch (error) {
      console.error("Error:", error.response?.data || error.message);
      throw error;
    }
  }

  async updateAssignee(user_id, status) {
    try {
      const { data } = await api.put(
        `/assignment/update/assignee-status/${user_id}`,
        {
          status,
        }
      );
      return data.message;
    } catch (error) {
      console.error("Error:", error.response?.data || error.message);
      throw error;
    }
  }

  async textAgent(query, created_by, callBack) {
    const { data } = await api.post(
      `/agent/text`,
      {
        created_by,
        query
      }
    );
    callBack()
    return data.message;
  } catch(error) {
    console.error("Error:", error.response?.data || error.message);
    throw error;
  }
}

$(document).ready(async function () {
  const assignmentService = new AssignmentService();
  const $select = $("#select-students");
  const $selectedItems = $("#selected-items");

  let allOptions = [];
  let selectedStudents = [];

  const authUserClass = new AuthUser();

  try {
    await authUserClass.checkAuth();
  } catch (e) {
    window.alert(e);
  }

  async function initialize() {
    try {
      const { data: studentsPayload } = await api.get("/user/get-students");
      const students = studentsPayload.payload;
      populateSelectStudentsElement(students);
      setAssignments();
    } catch (error) {
      console.error("Error loading students", error);
    }
  }

  async function setAssignments() {
    try {
      const assignments = await assignmentService.getAssignments(
        authUserClass.user_id
      );
      populateTasks(assignments);
    } catch (error) {
      console.error("Error loading students", error);
    }
  }

  function populateSelectStudentsElement(students) {
    $select.empty();
    $select.append(`<option disabled selected>Select Students</option>`);
    allOptions = [];

    students.forEach((student) => {
      const fullName = `${student.first_name} ${student.last_name}`;
      allOptions.push({ value: student.user_id, text: fullName });

      $select.append(`<option value="${student.user_id}">${fullName}</option>`);
    });
  }

  function populateTasks(assignments) {
    const $template = $("#task-template");
    const $tbody = $("#table-body");
    $tbody.empty();

    assignments.forEach((assignment, index) => {
      const $clone = $($template.html());

      $clone.find(".row-id").text(index + 1);
      $clone.find(".row-title").text(assignment.title);
      $clone.find(".row-description").text(assignment.description);
      $clone.find(".row-due_date").text(assignment.due_date);
      $clone.find(".btn-error").on("click", function () {
        if (confirm("Are you sure you want to delete this task?")) {
          $clone.remove();
          (async () => {
            const message = await assignmentService.deleteAssignments(
              assignment.assignment_id
            );
            console.log(message);
          })();
        }
      });
      $clone.find(".btn-info").on("click", function () {
        populateAssignedStudentTable(assignment.assignees, assignment.due_date);
        $("#showSubmit")[0].showModal();
      });
      $tbody.append($clone);
    });
  }

  async function populateAssignedStudentTable(studentList, due_date) {
    try {
      const tbody = $("#assigned-student-tbody");
      const template = $("#assigned-student-template");
      tbody.empty();

      if (!studentList || studentList.length === 0) {
        tbody.append(`
          <tr>
            <td colspan="5" class="text-center text-gray-500 py-4">
              No assigned students found.
            </td>
          </tr>
        `);
        return;
      }

      const dueDate = new Date(due_date);

      studentList.forEach((student) => {
        const newRow = template.contents().clone();

        newRow.find(".row-id").text(student.assigned_task_id);
        newRow
          .find(".row-name")
          .text(`${student.first_name} ${student.last_name}`);
        newRow
          .find(".row-url")
          .html(
            student.attachment_url
              ? isValidUrl(student.attachment_url)
                ? `<a href="${student.attachment_url}" target="_blank" class="link text-primary">View</a>`
                : `<a href="${submittedFileBaseUrl}${student.attachment_url}" target="_blank" class="link text-primary">View</a>`
              : "No file"
          );

        const submittedAt = student.submitted_at
          ? new Date(student.submitted_at)
          : null;

        let submittedText = student.submitted_at
          ? formatDueDateWithAMPM(student.submitted_at)
          : "-";

        if (
          student.task_status !== "Complete" &&
          submittedAt &&
          submittedAt > dueDate
        ) {
          submittedText += " (Done Late)";
        }
        newRow.find(".row-submitted_at").text(submittedText);

        const statusBadge = newRow.find(".row-status .badge");
        const taskStatus = student.task_status;

        let badgeText = "";
        let badgeClass = "";

        switch (taskStatus) {
          case "Complete":
            badgeText = "Complete";
            badgeClass = "badge-success";
            break;
          case "Submitted":
            badgeText = "Submitted";
            badgeClass = "badge-info";
            break;
          case "Late":
            badgeText = "Late";
            badgeClass = "badge-error";
            break;
          case "Pending":
          default:
            badgeText = "Pending";
            badgeClass = "badge-warning";
            break;
        }

        statusBadge
          .text(badgeText)
          .removeClass("badge-success badge-error badge-warning badge-info")
          .addClass(badgeClass);

        const actionBtn = newRow.find(".btn-success");

        const isLate = submittedAt && submittedAt > dueDate;

        if (
          taskStatus === "Complete" ||
          taskStatus === "Late" ||
          taskStatus === "Pending"
        ) {
          actionBtn
            .prop("disabled", true)
            .addClass("opacity-50 cursor-not-allowed");
        } else if (taskStatus === "Submitted") {
          actionBtn
            .prop("disabled", false)
            .removeClass("opacity-50 cursor-not-allowed");

          actionBtn.off("click");

          actionBtn.on("click", async () => {
            const newStatus = isLate ? "Late" : "Complete";
            await updateAssignedTaskStatus(student.assigned_task_id, newStatus);
            await showSubmitStudent(student.task_id);
          });
        } else {
          actionBtn
            .prop("disabled", true)
            .addClass("opacity-50 cursor-not-allowed");
        }

        tbody.append(newRow);
      });
    } catch (error) {
      console.error("Error populating assigned students:", error);
    }
  }

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
    $select
      .empty()
      .append("<option disabled selected>Select Students</option>");
    allOptions.forEach((opt) => {
      if (!selectedStudents.some((s) => s.value === opt.value)) {
        $select.append(`<option value="${opt.value}">${opt.text}</option>`);
      }
    });
  }

  $select.on("change", function () {
    const val = $(this).val();
    const text = $(this).find("option:selected").text();

    if (val && !selectedStudents.some((s) => s.value === val)) {
      selectedStudents.push({ value: val, text });
      updateSelectOptions();
      renderSelected();
    }
  });

  $("#addManualAssignmentBtn").click(async function () {
    try {
      const title = $("#titleInput").val();
      const description = $("#descriptionInput").val();
      const due_date = $("#dueDateInput").val();
      const userIDs = selectedStudents.map((item) => item.value);

      const obj = {
        created_by: authUserClass.user_id,
        title,
        description,
        due_date,
        userIDs,
      };

      const message = await assignmentService.handleAddAssignment(obj);
      setAssignments();
      alert(message);
    } catch (error) {
      console.log(error);
    }
  });

  $("#aiForm").on('submit', async function (e) {
    e.preventDefault()
    const submitBtn = $(this).find('button[type="submit"]');

    toggleButtonLoading(submitBtn, true, "Loading...");
    const formData = new FormData(this)
    query = formData.get('query')
    created_by = authUserClass.user_id
    if (!query || !created_by) {
      return
    }

    try {
      const message = await assignmentService.textAgent(query, created_by, setAssignments);
      console.log(message)
    } catch (error) {
      console.log(error);
    } finally {
      toggleButtonLoading(submitBtn, false);
    }
  })

  initialize();
});
