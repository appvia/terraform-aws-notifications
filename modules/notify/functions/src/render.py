from typing import Any, Dict, Optional, Union, Self

class Render:
  """
  Base class for vendor specific renders
  """
  def __init__(self: Self):
    pass
  
  """
  Must override this method
  """
  def payload(
    parsedMessage: Union[str, Dict],
    originalMessage: Union[str, Dict],
    subject: Optional[str] = None,
) -> Dict:
    raise NotImplementedError