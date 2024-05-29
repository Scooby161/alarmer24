document.addEventListener('DOMContentLoaded', function() {
    $.fn.dataTable.ext.type.order['datetime-custom-pre'] = function (d) {
    return moment(d, 'DD/MM/YY HH:mm').unix();
};
	var table = $('#emailTable').DataTable({
        "paging": false,
        "searching": true,
        "info": false,
        order: [[5, 'desc']],
        columnDefs: [
    { visible: false, targets: 0, searchable: true },
    { width: '10%', targets: 6 },
    {
        targets: 5,
        type: 'datetime-custom' // Specify the data type as "date"
    }
],
         buttons: ['showSelected'],
        "rowCallback": function(row, data) {
            var colorMapping = {
                "high temp alarm": "#fc8686",
                "high t.alarm": "#fc8686",
                "sair error": "#fc8686",
                "sair": "#fc8686",
                "temp": "#fc8686",
                "high": "#fc8686",
                "high saction pressure": "#fc8686",
                "high condensing pressure": "#fc8686",
                "comm error": "#d193ed",
                "main": "#d193ed",
                "mode (main sw. off)": "#d193ed",
                "off": "#d193ed",
                "comm": "#d193ed",
                "comm": "#d193ed",
                "s5 error": "#fcef79",
                "s3 error": "#fcef79",
                "s4 error": "#fcef79",
                "s2 error": "#fcef79",
                "pe error": "#759bfa",
                "5 fault": "#759bfa",
                "door alarm": "#759bfa",
                "6 fault": "#759bfa",
                "case clean":"#d193ed",
                "offline":"#d193ed",
                "clean":"#d193ed",
                "case":"#d193ed",
                "mode":"#d193ed",
                "1a safety cut out":"#759bfa",
                "2a safety cut out":"#759bfa",
                "3a safety cut out":"#759bfa",
                "3 safety cut out":"#759bfa",
                "1 safety cut out":"#759bfa",
                "2 safety cut out":"#759bfa",
                "4a safety cut out":"#759bfa",
                "5a safety cut out":"#759bfa",
                "6a safety сut out":"#759bfa",
                "compr safety cutout lt":"#759bfa",
                "compr. safety cutout":"#759bfa",
                "comp":"#759bfa",
                "fan":"#759bfa",
                "1 fault":"#759bfa",
                "2 fault":"#759bfa",
                "3 fault":"#759bfa",
                "4 fault":"#759bfa",
                "low temp alarm":"#759bfa",
                "liquid level alarm":"#759bfa",
                "low suction pressure":"#759bfa",
                 "inject prob":"#759bfa",
                 "max def time": "#fcef79",
                 "offline block":"#d193ed",
                 "alarm 1":"#759bfa",
                 "zabbix":"#c6ff85",
                 "danfoss esk":"#c6ff85",
                 "danfoss stavholod":"#c6ff85",
                 "carel esk":"#c6ff85",
                 "carel stavholod":"#c6ff85",
                 "freetech":"#c6ff85",
                 "vkusvill":"#c6ff85",
                 "dixell":"#c6ff85",
                 "lenta":"#c6ff85",
                 "indis":"#c6ff85",
                 "ashan":"#c6ff85",
                 "upo magnit":"#c6ff85",
                 "aktyalnie zaivki":"#c6ff85",
                 "freon":"#c6ff85",

            };
            var status = data[3];
            var bgColor = colorMapping[status.toLowerCase()];
            if (bgColor) {
                $(row).css('background-color', bgColor);
            }
            var productName = data[1];
            if (productName.indexOf("Metro") !== -1) {
                $(row).find('td:first').css('background-color', "#194684");
                $(row).find('td:first').css('color', "white");
            }
        },

        initComplete: function () {
        this.api()
            .columns()
            .every(function () {
                let column = this;
                let title = column.footer().textContent;

                // Create input element
                let input = document.createElement('input');
                input.placeholder = title;
                column.footer().replaceChildren(input);

                // Event listener for user input
                input.addEventListener('keyup', () => {
                    if (column.search() !== this.value) {
                        column.search(input.value).draw();
                    }
                });
            });
    }

    });
});
   console.log('Initializing DataTable...');
$('#emailTable tbody tr').each(function() {
    console.log($(this).find('td').eq(5).text());
});

    $('#emailTable tbody').on('mouseenter', 'tr', function () {
        $(this).addClass('highlight');
    });

    $('#emailTable tbody').on('mouseleave', 'tr', function () {
        $(this).removeClass('highlight');
    });

    function addNewTextON(input) {
        var newText = $(input).val();
        var row = $(input).closest('tr');
        var id = row.attr('title');
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
        var newText = $(button).prev('.newText').val();
        var row = $(button).closest('tr');
        var id = row.attr('title');

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
        addcolortostatus(select);
        var selectedValue = $(select).find('option:selected').text();

        var row = $(select).closest('tr');
        var id = row.attr('title');

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
