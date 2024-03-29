$(document).ready(function() {
    var table = $('#emailTable').DataTable({
        "paging": false,
        "searching": true,
        "info": false,
        order: [[5, 'desc']],
        "rowCallback": function(row, data) {
            if (data[3] == "High Temp Alarm") {
                $(row).css('background-color', '#F08080');
            } else if (data[3] == "S5 Error") {
                $(row).css('background-color', '#F0E68C');
            } else if (data[3] == "OFFLINE") {
                $(row).css('background-color', '#7B68EE');
            } else if (data[3] == "Pe Error"){
                $(row).css('background-color', '#4682B4');
            }else if (data[3] == "5 Fault"){
                $(row).css('background-color', '#4682B4');
            }else if (data[3] == "Door Alarm"){
                $(row).css('background-color', '#F0E68C');
            }else if (data[3] == "6 Fault"){
                $(row).css('background-color', '#4682B4');
            }

        }
    });
});
    $('#emailTable tbody').on('mouseenter', 'tr', function () {
        $(this).addClass('highlight');
    });

    $('#emailTable tbody').on('mouseleave', 'tr', function () {
        $(this).removeClass('highlight');
    });

            function addNewTextON(input) {
    var newText = $(input).val();  // Получаем значение input, на котором произошло изменение
    var row = $(input).closest('tr');
    var id = row.find('td:first').text();

    fetch('/update-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: id, newText: newText }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Update successful', data);
        row.find('td:nth-last-child(3)').text(newText);
    })
    .catch(error => {
        console.error('Update failed', error);
    });
}


        function addNewText(button) {
    var newText = $(button).prev('.newText').val();  // Получаем значение input в текущей строке
    var row = $(button).closest('tr');
    var id = row.find('td:first').text();

    fetch('/update-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: id, newText: newText }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Update successful', data);
        row.find('td:nth-last-child(3)').text(newText);
    })
    .catch(error => {
        console.error('Update failed', error);
    });
}
function addcolortostatus(select) {
      var selectedValue = select.value;
      select.className = selectedValue;
    }
function addStatus(select) {
addcolortostatus(select)
    var selectedValue = $(select).find('option:selected').text();

    var row = $(select).closest('tr');
    var id = row.find('td:first').text();
    console.log(id,selectedValue);
    fetch('/update-status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: id, selectedValue: selectedValue }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Update successful', data);
    })
    .catch(error => {
        console.error('Update failed', error);
    });
    }
   document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('rootLinkButton').onclick = function() {
    window.location.href = "/active";
};
document.getElementById('falseLinkButton').onclick = function() {
    window.location.href = "/false";
};
document.getElementById('deviceLinkButton').onclick = function() {
    window.location.href = "/devices";
};

    });