class StudentService {
  async fetchAssignments(user_id) {
    try {
      const { data } = await api.get(
        `/assignment/student-assignments/${user_id}`
      );
      return data.payload;
    } catch (error) {
      console.error("Error:", error.response?.data || error.message);
      throw error;
    }
  }
}

$(document).ready(async function () {
  checkConnection();
  const authUserClass = new AuthUser();

  try {
    await authUserClass.checkAuth();
    console.log("Current User", authUserClass.getUserObj);
  } catch (e) {
    window.alert(e);
  }

  async function fetchAssignments() {
    const studentService = new StudentService();
    try {
      const data = await studentService.fetchAssignments(
        authUserClass.getUserObj.user_id
      );
      const assignments = Array.isArray(data) ? data : [data];
      const $tableBody = $("#table-body");
      const $template = $($("#assignment-row-template").html());

      $tableBody.empty();

      assignments.forEach((assignment, index) => {
        const $clone = $template.clone();
        $clone.find(".index").text(index + 1);
        $clone.find(".title").text(assignment.title);
        $clone.find(".description").text(assignment.description);
        $clone
          .find(".due-date")
          .text(new Date(assignment.due_date).toLocaleDateString());

        $tableBody.append($clone);
      });
    } catch (error) {
      console.error("Failed to fetch assignments:", error);
    }
  }

  fetchAssignments();
});
