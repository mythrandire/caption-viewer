"""
Caption Viewer Operator(s)

| Copyright 2017-2025, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import fiftyone as fo
import fiftyone.operators as foo
import fiftyone.operators.types as types
import fiftyone.core.view as fov


class CaptionViewerPanel(foo.Panel):
    @property
    def config(self):
        return foo.PanelConfig(
            name="caption_viewer_panel",
            label="Caption Viewer",
            surfaces="modal",
            allow_multiple=True,
        )

    def on_load(self, ctx):
        selected_field = ctx.panel.state.selected_field
        if not selected_field:
            # No field selected yet, do nothing special
            ctx.panel.state.empty_state = (
                "No field selected"
            )
            return

        # If we have a selected field, retrieve its value for the current sample
        sample_id = ctx.current_sample

        # Create a simple view for just this one sample
        view = fov.make_optimized_select_view(ctx.view, [sample_id])
        sample = ctx.view[sample_id]  # single sample in this view

        # Fetch the field value
        field_value = sample[selected_field]

        # Store the fetched field value in state
        ctx.panel.state.display_text = str(field_value)

    def render(self, ctx):
        # Get the valid string-type fields for the current dataset
        valid_fields = _get_string_fields(ctx)

        if not ctx.panel.state.selected_field:
            empty_state = types.Object()
            empty_state.enum(
                "field_selector",
                valid_fields,
                label="Select a field to display",
                on_change=self.on_field_select,
            )
            return types.Property(
                empty_state,
                view=types.GridView(
                    align_x="center",
                    align_y="center",
                    orientation="vertical",
                    height=100,
                ),
            )
        
        panel = types.Object()

        if len(valid_fields):
            selected_field = ctx.panel.state.get(
                "selected_field", valid_fields[0]
            )
            if selected_field:
                menu = panel.menu("menu", overlay="top-right")
                menu.enum(
                    "field_selector",
                    valid_fields,
                    label="Select a field",
                    default=selected_field,
                    on_change=self.on_field_select,
                )
                # Show the string value fetched in on_load()
                display_text = ctx.panel.state.get("display_text", "")
                panel.md(f"**Value**: \n\n {display_text}")

        return types.Property(
            panel, view=types.GridView(height=100, width=100)
        )

    def on_field_select(self, ctx):
        field_name = ctx.params.get("value")
        ctx.panel.state.selected_field = field_name
        ctx.panel.set_title(f"Caption Viewer: {field_name}")

        self.on_load(ctx)

    def on_change_current_sample(self, ctx):
        self.on_load(ctx)


def _get_string_fields(ctx):
    """
    Utility to return a list of string fields from the dataset.
    """
    dataset = ctx.view._dataset  # or ctx.view.dataset
    schema = dataset.get_field_schema(flat=True)  # top-level fields

    # Filter for only string-type fields
    str_fields = [
        name for name, field in schema.items()
        if isinstance(field, fo.StringField)
    ]

    return str_fields


def register(p):
    p.register(CaptionViewerPanel)