$(document).ready(function () {
  const authUserClass = new AuthUser();

  const rowTemplate = $("#row-template");
  const tableBody = $("#table-body");

  try {
    authUserClass.checkAuth();
  } catch (e) {
    window.alert(e);
  }

  async function initialize() {
    try {
      const { data: studentsPayload } = await api.get("/user/get-students");
      const students = studentsPayload.payload;
      populateAdminDashboardTable(students);
      populateSelectStudentsElement(students);
    } catch (error) {}
  }
  initialize();

  function populateAdminDashboardTable(students) {
    students.forEach((student) => {
      const clone = $(rowTemplate.get(0).content).clone();

      clone.find(".row-index").text(student.user_id);
      const fullName = `${student.first_name} ${student.last_name}`;
      clone.find(".row-fullname").text(fullName);

      const avatarImg = clone.find(".row-avatar");
      const profileUrl = student.profile_url;
      avatarImg.attr("src", profileUrl);

      clone.find(".row-email").text(student.email);
      clone.find(".row-phone").text(student.phone_number);
      clone.find(".row-gender").text(student.gender);
      clone.find(".row-course").text(student.course);
      clone.find(".row-address").text(student.address);
      clone.find(".row-age").text(calculateAge(student.birthdate));

      const statusBadge = clone.find(".row-status .badge");
      const isVerified = student.is_verified;
      statusBadge
        .text(isVerified ? "Verified" : "Not Verified")
        .removeClass("badge-success badge-error")
        .addClass(isVerified ? "badge-success" : "badge-error");

      tableBody.append(clone);
    });
  }

  const selectStudentsElement = $("#select-students").get(0);
  const studentOptionTemplate = $("#student-option-template").get(0);

  function populateSelectStudentsElement(students) {
    students.forEach((student) => {
      console.log(student);
      const clone = studentOptionTemplate.content.cloneNode(true);
      const option = clone.querySelector("option");
      option.value = student.user_id;
      option.textContent = student.first_name + " " + student.last_name;
      selectStudentsElement.appendChild(option);
    });
  }
});
