from typing import List, Any


class TestActivationTriggersClass:
    pass

    def __init__(self, ) -> None:
        pass


class DynamicFilterValue:
    name: str
    id: str
    count: int
    selected: bool
    enabled: bool

    def __init__(self, name: str, id: str, count: int, selected: bool, enabled: bool) -> None:
        self.name = name
        self.id = id
        self.count = count
        self.selected = selected
        self.enabled = enabled


class Filter:
    selected: bool
    values: List[DynamicFilterValue]
    id: str
    name: str
    collapsed: bool
    type: str
    parameter: str
    event_action: str
    enabled: bool
    action_tokens: List[Any]

    def __init__(self, selected: bool, values: List[DynamicFilterValue], id: str, name: str, collapsed: bool, type: str, parameter: str, event_action: str, enabled: bool, action_tokens: List[Any]) -> None:
        self.selected = selected
        self.values = values
        self.id = id
        self.name = name
        self.collapsed = collapsed
        self.type = type
        self.parameter = parameter
        self.event_action = event_action
        self.enabled = enabled
        self.action_tokens = action_tokens


class BusinessStructure:
    home_furnishing_business_name: str
    home_furnishing_business_no: str
    product_area_name: str
    product_area_no: str
    product_range_area_name: str
    product_range_area_no: str

    def __init__(self, home_furnishing_business_name: str, home_furnishing_business_no: str, product_area_name: str, product_area_no: str, product_range_area_name: str, product_range_area_no: str) -> None:
        self.home_furnishing_business_name = home_furnishing_business_name
        self.home_furnishing_business_no = home_furnishing_business_no
        self.product_area_name = product_area_name
        self.product_area_no = product_area_no
        self.product_range_area_name = product_range_area_name
        self.product_range_area_no = product_range_area_no


class CategoryPath:
    name: str
    key: str

    def __init__(self, name: str, key: str) -> None:
        self.name = name
        self.key = key


class Color:
    name: str
    id: int
    hex: int

    def __init__(self, name: str, id: int, hex: int) -> None:
        self.name = name
        self.id = id
        self.hex = hex


class GprDescription:
    number_of_variants: int
    variants: List[Any]

    def __init__(self, number_of_variants: int, variants: List[Any]) -> None:
        self.number_of_variants = number_of_variants
        self.variants = variants


class OptimizelyAttributes:
    product_type: str

    def __init__(self, product_type: str) -> None:
        self.product_type = product_type


class Current:
    prefix: str
    whole_number: int
    separator: str
    decimals: str
    suffix: str
    is_regular_currency: bool

    def __init__(self, prefix: str, whole_number: int, separator: str, decimals: str, suffix: str, is_regular_currency: bool) -> None:
        self.prefix = prefix
        self.whole_number = whole_number
        self.separator = separator
        self.decimals = decimals
        self.suffix = suffix
        self.is_regular_currency = is_regular_currency


class SalesPrice:
    currency_code: str
    numeral: float
    current: Current
    is_breath_taking: bool
    discount: str
    tag: str
    price_text: str

    def __init__(self, currency_code: str, numeral: float, current: Current, is_breath_taking: bool, discount: str, tag: str, price_text: str) -> None:
        self.currency_code = currency_code
        self.numeral = numeral
        self.current = current
        self.is_breath_taking = is_breath_taking
        self.discount = discount
        self.tag = tag
        self.price_text = price_text


class Product:
    name: str
    type_name: str
    item_measure_reference_text: str
    main_image_url: str
    pip_url: str
    filter_class: str
    id: int
    item_no_global: int
    online_sellable: bool
    last_chance: bool
    gpr_description: GprDescription
    colors: List[Color]
    tag: str
    quick_facts: List[Any]
    features: List[Any]
    availability: List[Any]
    rating_value: float
    rating_count: int
    item_no: int
    item_type: str
    sales_price: SalesPrice
    contextual_image_url: str
    main_image_alt: str
    business_structure: BusinessStructure
    category_path: List[CategoryPath]
    valid_design_text: str
    hero_backoff_data: TestActivationTriggersClass
    optimizely_attributes: OptimizelyAttributes

    def __init__(self, name: str, type_name: str, item_measure_reference_text: str, main_image_url: str, pip_url: str, filter_class: str, id: int, item_no_global: int, online_sellable: bool, last_chance: bool, gpr_description: GprDescription, colors: List[Color], tag: str, quick_facts: List[Any], features: List[Any], availability: List[Any], rating_value: float, rating_count: int, item_no: int, item_type: str, sales_price: SalesPrice, contextual_image_url: str, main_image_alt: str, business_structure: BusinessStructure, category_path: List[CategoryPath], valid_design_text: str, hero_backoff_data: TestActivationTriggersClass, optimizely_attributes: OptimizelyAttributes) -> None:
        self.name = name
        self.type_name = type_name
        self.item_measure_reference_text = item_measure_reference_text
        self.main_image_url = main_image_url
        self.pip_url = pip_url
        self.filter_class = filter_class
        self.id = id
        self.item_no_global = item_no_global
        self.online_sellable = online_sellable
        self.last_chance = last_chance
        self.gpr_description = gpr_description
        self.colors = colors
        self.tag = tag
        self.quick_facts = quick_facts
        self.features = features
        self.availability = availability
        self.rating_value = rating_value
        self.rating_count = rating_count
        self.item_no = item_no
        self.item_type = item_type
        self.sales_price = sales_price
        self.contextual_image_url = contextual_image_url
        self.main_image_alt = main_image_alt
        self.business_structure = business_structure
        self.category_path = category_path
        self.valid_design_text = valid_design_text
        self.hero_backoff_data = hero_backoff_data
        self.optimizely_attributes = optimizely_attributes


class Item:
    metadata: str
    product: Product
    type: str
    label: str
    action_tokens: List[Any]
    is_breakout: bool

    def __init__(self, metadata: str, product: Product, type: str, label: str, action_tokens: List[Any], is_breakout: bool) -> None:
        self.metadata = metadata
        self.product = product
        self.type = type
        self.label = label
        self.action_tokens = action_tokens
        self.is_breakout = is_breakout


class ItemsPerType:
    product: int

    def __init__(self, product: int) -> None:
        self.product = product


class ResultMetadata:
    start: int
    end: int
    max: int
    items_per_type: ItemsPerType

    def __init__(self, start: int, end: int, max: int, items_per_type: ItemsPerType) -> None:
        self.start = start
        self.end = end
        self.max = max
        self.items_per_type = items_per_type


class SortOrdersValue:
    id: str
    name: str
    event_action: str
    selected: bool

    def __init__(self, id: str, name: str, event_action: str, selected: bool) -> None:
        self.id = id
        self.name = name
        self.event_action = event_action
        self.selected = selected


class SortOrders:
    name: str
    values: List[SortOrdersValue]

    def __init__(self, name: str, values: List[SortOrdersValue]) -> None:
        self.name = name
        self.values = values


class Result:
    component: str
    view_mode: str
    filters: List[Filter]
    dynamic_filters: List[Filter]
    items: List[Item]
    sort_orders: SortOrders
    metadata: ResultMetadata

    def __init__(self, component: str, view_mode: str, filters: List[Filter], dynamic_filters: List[Filter], items: List[Item], sort_orders: SortOrders, metadata: ResultMetadata) -> None:
        self.component = component
        self.view_mode = view_mode
        self.filters = filters
        self.dynamic_filters = dynamic_filters
        self.items = items
        self.sort_orders = sort_orders
        self.metadata = metadata


class Welcome9:
    usergroup: str
    results: List[Result]
    test_activation_triggers: TestActivationTriggersClass
    metadata: TestActivationTriggersClass

    def __init__(self, usergroup: str, results: List[Result], test_activation_triggers: TestActivationTriggersClass, metadata: TestActivationTriggersClass) -> None:
        self.usergroup = usergroup
        self.results = results
        self.test_activation_triggers = test_activation_triggers
        self.metadata = metadata
