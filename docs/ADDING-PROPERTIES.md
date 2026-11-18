# Adding a property listing

Listings on the Real Estate page are read from `data/properties.json`. The generator does not invent a listing. An entry appears on the site only when `published` is `true`.

The file already contains one entry, `example-limassol-apartment`, with `published` set to `false`. That entry is a format sample. It is not a property for sale. Leave it unpublished, or delete it once a real listing exists. Do not set it to `published: true` unless the text and the photograph are a real instruction you intend to show.

## Add an entry

Copy the example object inside the `listings` array and change the fields.

| Field | What to put |
| --- | --- |
| `id` | The page address. Lower case letters, digits and hyphens, for example `limassol-germasogeia-apartment`. It becomes `/real-estate/<id>/`, `/ru/real-estate/<id>/` and `/el/real-estate/<id>/`. Do not change an id after the page has been shared. |
| `published` | `true` to show the listing. `false` to keep it in the file and off the site. Only the JSON boolean `true` publishes it. |
| `title` | An object with `en`, `ru` and `el`. |
| `type` | One of `project`, `apartment`, `villa`, `house`, `land`, `commercial`. |
| `city` | Town or city, as you want it shown. The same text is used in every language. |
| `area` | Neighbourhood or village. Optional. Leave it as `""` if you have no smaller place name. |
| `price_eur` | A number in euro, such as `350000`. Use `null` if you are not stating a price. |
| `price_from` | `true` if the number is a starting price (“from”). `false` if it is the stated price. |
| `bedrooms` | A whole number, or `null`. |
| `area_m2` | Covered or buildable area in square metres, as a number, or `null`. |
| `status` | One of `available`, `sold`, `under-construction`. |
| `description` | An object with `en`, `ru` and `el`. State only what you know. Do not invent a yield, a view, or a completion date. |
| `photos` | A list of paths. Each path must start with `images/properties/<id>/`. The first path is the picture on the card. |

Put the image files in `images/properties/<id>/` before you set `published` to `true`. A published listing whose picture is missing stops the build. An unpublished sample may name a picture that is not there yet. The example does that with `cover.jpg`.

A push of `data/properties.json` or `images/` to `main` rebuilds the site. Published listings are added to `sitemap.xml` in English, Russian and Greek. An unpublished entry is not built and is not in the sitemap. When nothing is published, the Real Estate page says that no properties are listed.

## Calculators

On each published listing that has a `price_eur`, the page links to four calculators with that price filled in:

- transfer fees: `?value=`
- VAT on a new property: `?price=` and, when `area_m2` is set, `&area=`
- stamp duty: `?value=`
- mortgage payment: `?principal=`

The mortgage link uses the price as the loan amount only so the calculator opens on a figure. It is not a statement of how much a bank will lend. VAT and transfer fees are alternatives on many purchases. The calculators explain that. The listing does not add them together.

Each listing page has its own request form. It posts to the same FormSubmit address as the contact page, info@mycytax.com. The button on the card and the button under the title both go to that form. The consultation buttons under the form are the same ones used on the guides. They go to the contact form.
