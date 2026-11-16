"""Author the current object's Blender construction here; do not import a prior model."""
import bpy


def build(spec, parameters):
    # Return a bpy.types.Collection linked to the active scene.
    # Every model object needs obj['part_id']; each expected part has exactly one anchor
    # with obj['part_anchor'] = True. Detail objects share their owner's part_id.
    # Model coordinates: Z up, -Y front. Use parameters for dimensions and interfaces.
    raise NotImplementedError('Inspect the supplied references and implement this model first.')
