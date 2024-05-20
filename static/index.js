const form = document.getElementById('student-form');
const formClassAttendance = document.getElementById('form-class-attendance');
const studentList = document.getElementById('student-list');
const studentListPackages = document.getElementById('student-list-packages');
const searchInput = document.getElementById('search-input');
const searchInput2 = document.getElementById('search-input-2');
const modalIdInput = document.querySelector("#modal #id");
const modalNameInput = document.querySelector("#modal #name");
const modalForm = document.querySelector("form#modal");
const date = document.querySelector('#date')
let attendanceData = [];

if (formClassAttendance){
  formClassAttendance.addEventListener('submit', () => {
    fetch('/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(attendanceData),
    })
      .then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.error(error));
  })
}

function toggleButton(btn) {
  if (date.value === '') {
    alert("Select a date first")
  }else{
    // Get the button's data-id
    const id = parseInt(btn.dataset.id);
    const newDate = date.value

    // Check if the id is already in the attendanceArray
    const index = attendanceData.findIndex(
      (attendance) => attendance.id === id
    );

    // If the id is not in the array, add it and toggle the button class
    if (index === -1) {
      attendanceData.push({id, newDate});
      btn.classList.add("btn-primary");
    } 
    // If the id is already in the array, remove it and toggle the button class
    else {
      attendanceData.splice(index, 1);
      btn.classList.remove("btn-primary");
    }
  }
}

function submit() {
  
}

if (studentListPackages) {
  const studentEls = studentListPackages.querySelectorAll("button")
  studentEls.forEach((student) => {
    student.addEventListener("click", () => {
      toggleButton(student);
    });
  });
}

function search(input, list) {
  const searchTerm = input.value.toLowerCase();
  const buttons = list.getElementsByTagName('button');
  Array.prototype.forEach.call(buttons, (button) => {
      const studentName = button.textContent.toLowerCase();
      if (studentName.includes(searchTerm)) {
          button.style.display = 'block';
        } else {
          button.style.display = 'none';
      }
  });
}

if (searchInput2) {
  searchInput2.addEventListener('input', () => {
  search(searchInput2, studentListPackages)
  });
  searchInput2.addEventListener('reset', () => {
    searchInput2.reset()
  });
}
if (studentList) {
  const studentsEls = studentList.querySelectorAll("button");
  studentsEls.forEach((student) => {
    student.addEventListener('click', function(e){
      modalForm.reset();
      const id = e.currentTarget.dataset.id;
      const name = e.currentTarget.dataset.name;
      modalIdInput.value = id;
      modalNameInput.value = name;
    })
  });
}


if (searchInput){
  searchInput.addEventListener('input', () => {
    search(searchInput, studentList)
  });
  searchInput.addEventListener('reset', () => {
    searchInput.reset()
  });
}
