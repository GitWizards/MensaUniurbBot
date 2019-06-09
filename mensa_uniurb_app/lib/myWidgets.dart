import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:intl/intl.dart';

class DataPicker extends StatefulWidget {
  DataPicker({@required this.setFunc});

  final Function setFunc;

  @override
  _DataPickerState createState() => _DataPickerState();
}

class _DataPickerState extends State<DataPicker> {
  String date = DateFormat('dd/MM/yyyy').format(DateTime.now());

  @override
  Widget build(BuildContext context) {
    return Container(
      child: RaisedButton(
        child: Row(
          children: <Widget>[
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Text(
                date,
                style: TextStyle(
                  fontSize: 25,
                  color: Colors.white,
                  shadows: <Shadow>[
                    Shadow(
                      color: Colors.black54,
                      offset: Offset(2.0, 2.0),
                      blurRadius: 5.0,
                    )
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Icon(
                Icons.date_range,
                color: Colors.white,
              ),
            ),
          ],
          mainAxisAlignment: MainAxisAlignment.center,
        ),
        shape: StadiumBorder(),
        color: Colors.blue,
        disabledColor: Colors.grey,
        onPressed: () => _showDateTimePicker(context),
      ),
      width: MediaQuery.of(context).size.width * 0.85,
      height: MediaQuery.of(context).size.height * 0.09,
    );
  }

  _showDateTimePicker(BuildContext context) async {
    DateTime selected;
    DateTime today = DateTime.now();
    Duration week = Duration(days: 7);

    selected = await showDatePicker(
      context: context,
      initialDate: today,
      firstDate: today,
      lastDate: today.add(week),
    );

    setState(() {
      if (selected != null) {
        date = DateFormat('dd/MM/yyyy').format(selected);
        widget.setFunc(DateFormat('MM-dd-yyyy').format(selected));
      }
    });
  }
}

class RadioButtons extends StatefulWidget {
  RadioButtons({
    @required this.textButton1,
    @required this.valueButton1,
    @required this.textButton2,
    @required this.valueButton2,
    @required this.setFunc,
  });

  final String textButton1;
  final String textButton2;
  final String valueButton1;
  final String valueButton2;
  final Function setFunc;

  @override
  _RadioButtonsState createState() => _RadioButtonsState();
}

class _RadioButtonsState extends State<RadioButtons> {
  bool selected = true;

  @override
  Widget build(BuildContext context) {
    return Row(
      // Select kitchen
      children: <Widget>[
        _singleButton(
            context, widget.textButton1, widget.valueButton1, selected),
        _singleButton(
            context, widget.textButton2, widget.valueButton2, !selected),
      ],
      mainAxisAlignment: MainAxisAlignment.center,
    );
  }

  Widget _singleButton(context, text, value, active) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Container(
        child: RaisedButton(
          child: Text(
            text,
            style: TextStyle(
              fontSize: 25,
              color: Colors.white,
              shadows: <Shadow>[
                Shadow(
                  color: Colors.black54,
                  offset: Offset(2.0, 2.0),
                  blurRadius: 5.0,
                )
              ],
            ),
          ),
          shape: StadiumBorder(),
          color: Colors.blue,
          disabledColor: Colors.grey,
          onPressed: active ? null : () => _changeActiveButton(),
        ),
        width: MediaQuery.of(context).size.width * 0.4,
        height: MediaQuery.of(context).size.height * 0.08,
      ),
    );
  }

  _changeActiveButton() {
    setState(() {
      selected = !selected;

      if (selected)
        widget.setFunc(widget.valueButton1);
      else
        widget.setFunc(widget.valueButton2);
    });
  }
}
