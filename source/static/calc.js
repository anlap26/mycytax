(function () {
  "use strict";
  var root = document.getElementById("calc");
  if (!root) return;
  var kind = root.getAttribute("data-calc");
  var htmlLang = document.documentElement.lang;
  var lang = htmlLang === "ru" || htmlLang === "el" ? htmlLang : "en";
  var T = {
    en: {
      value: "Accepted value (EUR)",
      price: "Price before VAT (EUR)",
      vatYes: "VAT is charged on this purchase",
      vatNo: "VAT is not charged (typical resale)",
      forced: "Seller acquired the property in a forced sale (Parts VI / VIA, Law 9/1965). The 50% reduction does not apply.",
      late: "The contract was not deposited at the Land Registry within six months (DLS leaflet: transfer fees increased by 10%).",
      buyers: "Equal buyers (fees are worked out on each share)",
      yearNew: "At least one party will sign on or after 1 January 2026",
      yearOld: "At least one party signed on or before 31 December 2025",
      area: "Buildable area (m²)",
      home: "Claiming the 5% rate as a primary and permanent residence",
      disability: "Eligible person with a disability (5% on the first 190 m²; the 190 m² ceiling on total area does not apply). Value limits are still applied. Confirm eligibility with the Tax Department.",
      sale: "Sale proceeds (EUR)",
      cost: "Acquisition and improvement cost, before indexation (EUR)",
      ratio: "Official indexation ratio (1 = no uplift). Take the ratio from the Tax Department inflation table. Do not guess it.",
      sellCosts: "Disposal costs not indexed (legal fees, agent, and so on) (EUR)",
      exNone: "No lifetime exemption (company, or allowance already used)",
      exGen: "General individual exemption, €30,000",
      exAgri: "Agricultural land sold by a farmer, €50,000",
      exHome: "Main residence exemption, €150,000",
      used: "Exemption already used in earlier disposals (EUR)",
      rent: "Annual gross rent (EUR)",
      otherInc: "Other taxable income this year, before this rent (EUR)",
      extra: "Other deductible costs of this letting, excluding the 20% statutory deduction (EUR)",
      purchase: "Price paid for the property (EUR)",
      principal: "Loan amount (EUR)",
      rate: "Annual interest rate (%)",
      years: "Term (years)",
      calc: "Calculate",
      result: "Result",
      note: "This is an illustration, not an assessment.",
      perBuyer: "Per buyer",
      fullScale: "Scale before any reduction",
      after: "After the rule selected above",
      band: "Band",
      duty: "Stamp duty",
      zero: "Stamp duty on this document is €0.",
      vat5: "Amount taxed at 5%",
      vat19: "Amount taxed at 19%",
      vatTotal: "VAT",
      ineligible: "On these figures the 5% rate is not available. VAT is 19% of the whole price.",
      notClaimed: "Without a primary-residence claim, VAT is 19% of the whole price.",
      gain: "Gain after indexation and disposal costs",
      exempt: "Exemption applied to this sale",
      taxable: "Taxable gain",
      cgt: "Capital gains tax at 20%",
      grossYield: "Gross yield",
      deduction: "20% statutory deduction",
      rentalProfit: "Rental amount put into the income-tax computation",
      incomeTax: "Income tax caused by that rental amount",
      ghs: "GHS at 2.65% of gross rent (no annual ceiling is applied here)",
      sdc: "Special Defence Contribution on this rent in 2026",
      netYield: "Yield after that income tax and GHS",
      monthly: "Monthly payment",
      totalPay: "Total paid over the term",
      interest: "Of which interest",
      schedule: "The payment assumes a fixed rate and a fully amortising loan, with no fees.",
      salary: "Other taxable income, apart from these dividends and this interest (EUR)",
      dividend: "Dividends (EUR)",
      interestAmt: "Interest (EUR)",
      profitNew: "Dividends are out of 2026 profits (domiciled rate 5%)",
      profitOld: "Dividends are from a Cyprus company, out of profits up to 2025, received by 31 December 2031 (domiciled rate 17%)",
      lowInc: "Total income is under €12,000, so domiciled interest is at 3% rather than 17%",
      nondomCol: "Not domiciled",
      domCol: "Domiciled",
      itax: "Income tax on the other income",
      sdcDiv: "Defence contribution on the dividends",
      sdcInt: "Defence contribution on the interest",
      totalTax: "Income tax plus those two contributions",
      sameBands: "The income-tax bands do not change with domicile.",
      profit: "Profit before this comparison (EUR)",
      shNon: "The shareholder is not domiciled",
      shDom: "The shareholder is domiciled, and the dividend is out of 2026 profits",
      cit: "Corporate tax at 15%",
      afterCit: "Paid out as a dividend after that corporate tax",
      coTotal: "Company route",
      seTax: "Self-employed route, income tax only",
      notSi: "Social insurance, GHS and expenses are not in either figure.",
      resale: "Resale: no VAT, transfer fees apply",
      newbuild: "New build: VAT is charged, so transfer fees are nil",
      vatPart: "VAT",
      transferPart: "Transfer fees",
      stampPart: "Stamp duty",
      purchaseTotal: "Those three together",
      notFees: "Lawyer, agent and local charges are not included.",
      incomeCmp: "Taxable income, or Portuguese rendimento coletável (EUR)",
      profitCmp: "Company profit (EUR)",
      uaeBand: "Euro amount of the UAE 0% band (AED 375,000). Use 0 to charge 9% on the whole profit.",
      otherRate: "A flat rate you supply for another country (%). Use 0 to skip it.",
      cyPerson: "Cyprus income tax",
      ptPerson: "Portugal income tax, mainland 2026 scale",
      uaePerson: "UAE personal income tax",
      otherPerson: "Tax at the rate you typed",
      cyCo: "Cyprus corporate tax at 15%",
      mtCo: "Malta corporate tax at 35%, no refund",
      ptCo: "Portugal corporate tax at 19%, mainland",
      grCo: "Greece corporate tax at 22%",
      uaeCo: "UAE corporate tax",
      compareNote: "Malta’s 2026 personal bands and the Greek personal scale are not calculated. Social insurance is not included.",
      consult: "Want an exact calculation for your property? Get a free consultation"
    },
    el: {
      value: "Αποδεκτή αξία (EUR)",
      price: "Τιμή πριν τον ΦΠΑ (EUR)",
      vatYes: "Επιβάλλεται ΦΠΑ σε αυτή την αγορά",
      vatNo: "Δεν επιβάλλεται ΦΠΑ (συνήθης μεταπώληση)",
      forced: "Ο πωλητής απέκτησε το ακίνητο σε αναγκαστική πώληση (Μέρη VI / VIA, Νόμος 9/1965). Η μείωση 50% δεν εφαρμόζεται.",
      late: "Το συμβόλαιο δεν κατατέθηκε στο Κτηματολόγιο μέσα σε έξι μήνες (φυλλάδιο Κτηματολογίου: τα τέλη αυξάνονται κατά 10%).",
      buyers: "Ίσοι αγοραστές (τα τέλη υπολογίζονται στο μερίδιο του καθενός)",
      yearNew: "Τουλάχιστον ένα μέρος θα υπογράψει την 1η Ιανουαρίου 2026 ή αργότερα",
      yearOld: "Τουλάχιστον ένα μέρος υπέγραψε έως τις 31 Δεκεμβρίου 2025",
      area: "Δομήσιμο εμβαδόν (τ.μ.)",
      home: "Αίτηση συντελεστή 5% ως κύρια και μόνιμη κατοικία",
      disability: "Δικαιούχο άτομο με αναπηρία (5% στα πρώτα 190 τ.μ.· το όριο συνολικού εμβαδού 190 τ.μ. δεν ισχύει). Τα όρια αξίας εφαρμόζονται ακόμη. Επιβεβαιώστε το δικαίωμα στο Τμήμα Φορολογίας.",
      sale: "Έσοδα πώλησης (EUR)",
      cost: "Κόστος απόκτησης και βελτιώσεων, πριν την τιμαριθμική αναπροσαρμογή (EUR)",
      ratio: "Επίσημος λόγος τιμαριθμικής αναπροσαρμογής (1 = χωρίς προσαύξηση). Πάρτε τον από τον πίνακα πληθωρισμού του Τμήματος Φορολογίας. Μην τον μαντέψετε.",
      sellCosts: "Έξοδα διάθεσης χωρίς τιμαριθμική αναπροσαρμογή (δικηγόρος, μεσίτης κ.λπ.) (EUR)",
      exNone: "Χωρίς ισόβια απαλλαγή (εταιρεία, ή η απαλλαγή έχει ήδη χρησιμοποιηθεί)",
      exGen: "Γενική απαλλαγή φυσικού προσώπου, €30.000",
      exAgri: "Γεωργική γη που πωλεί γεωργός, €50.000",
      exHome: "Απαλλαγή κύριας κατοικίας, €150.000",
      used: "Απαλλαγή που έχει ήδη χρησιμοποιηθεί σε προηγούμενες διαθέσεις (EUR)",
      rent: "Ετήσιο ακαθάριστο ενοίκιο (EUR)",
      otherInc: "Άλλο φορολογητέο εισόδημα φέτος, πριν από αυτό το ενοίκιο (EUR)",
      extra: "Άλλα εκπιπτόμενα έξοδα αυτής της μίσθωσης, χωρίς τη νόμιμη έκπτωση 20% (EUR)",
      purchase: "Τιμή που πληρώθηκε για το ακίνητο (EUR)",
      principal: "Ποσό δανείου (EUR)",
      rate: "Ετήσιο επιτόκιο (%)",
      years: "Διάρκεια (έτη)",
      calc: "Υπολογισμός",
      result: "Αποτέλεσμα",
      note: "Αυτό είναι παράδειγμα, όχι βεβαίωση αρχής.",
      perBuyer: "Ανά αγοραστή",
      fullScale: "Κλίμακα πριν από μείωση",
      after: "Μετά τον κανόνα που επιλέξατε",
      band: "Κλιμάκιο",
      duty: "Χαρτόσημο",
      zero: "Το χαρτόσημο αυτού του εγγράφου είναι €0.",
      vat5: "Ποσό με 5%",
      vat19: "Ποσό με 19%",
      vatTotal: "ΦΠΑ",
      ineligible: "Με αυτά τα νούμερα ο συντελεστής 5% δεν είναι διαθέσιμος. Ο ΦΠΑ είναι 19% σε όλη την τιμή.",
      notClaimed: "Χωρίς αίτηση κύριας κατοικίας, ο ΦΠΑ είναι 19% σε όλη την τιμή.",
      gain: "Κέρδος μετά την τιμαριθμική αναπροσαρμογή και τα έξοδα διάθεσης",
      exempt: "Απαλλαγή που εφαρμόστηκε σε αυτή την πώληση",
      taxable: "Φορολογητέο κέρδος",
      cgt: "Φόρος κεφαλαιουχικών κερδών 20%",
      grossYield: "Μικτή απόδοση",
      deduction: "Νόμιμη έκπτωση 20%",
      rentalProfit: "Ποσό ενοικίου που μπαίνει στον υπολογισμό φόρου εισοδήματος",
      incomeTax: "Φόρος εισοδήματος που προκαλεί αυτό το ποσό",
      ghs: "ΓεΣΥ 2,65% επί του ακαθάριστου ενοικίου (δεν εφαρμόζεται ετήσιο ανώτατο εδώ)",
      sdc: "Έκτακτη εισφορά για την άμυνα σε αυτό το ενοίκιο το 2026",
      netYield: "Απόδοση μετά από αυτόν τον φόρο εισοδήματος και τη ΓεΣΥ",
      monthly: "Μηνιαία δόση",
      totalPay: "Σύνολο στη διάρκεια",
      interest: "Από αυτά, τόκοι",
      schedule: "Η δόση υποθέτει σταθερό επιτόκιο και πλήρη χρεολυσία, χωρίς έξοδα.",
      salary: "Άλλο φορολογητέο εισόδημα, εκτός από αυτά τα μερίσματα και αυτούς τους τόκους (EUR)",
      dividend: "Μερίσματα (EUR)",
      interestAmt: "Τόκοι (EUR)",
      profitNew: "Τα μερίσματα είναι από κέρδη του 2026 (συντελεστής με κατοικία 5%)",
      profitOld: "Τα μερίσματα είναι από κυπριακή εταιρεία, από κέρδη έως το 2025, εισπραχθέντα έως τις 31 Δεκεμβρίου 2031 (συντελεστής με κατοικία 17%)",
      lowInc: "Το συνολικό εισόδημα είναι κάτω από €12.000, οπότε οι τόκοι με κατοικία είναι στο 3% και όχι στο 17%",
      nondomCol: "Χωρίς κατοικία",
      domCol: "Με κατοικία",
      itax: "Φόρος εισοδήματος στο άλλο εισόδημα",
      sdcDiv: "Έκτακτη εισφορά στα μερίσματα",
      sdcInt: "Έκτακτη εισφορά στους τόκους",
      totalTax: "Φόρος εισοδήματος συν τις δύο εισφορές",
      sameBands: "Οι κλίμακες φόρου εισοδήματος δεν αλλάζουν με την κατοικία.",
      profit: "Κέρδος πριν από αυτή τη σύγκριση (EUR)",
      shNon: "Ο μέτοχος δεν έχει κατοικία",
      shDom: "Ο μέτοχος έχει κατοικία, και το μέρισμα είναι από κέρδη του 2026",
      cit: "Εταιρικός φόρος 15%",
      afterCit: "Πληρώνεται ως μέρισμα μετά από αυτόν τον εταιρικό φόρο",
      coTotal: "Οδός εταιρείας",
      seTax: "Οδός αυτοαπασχολούμενου, μόνο φόρος εισοδήματος",
      notSi: "Κοινωνικές ασφαλίσεις, ΓεΣΥ και έξοδα δεν είναι σε κανένα από τα δύο ποσά.",
      resale: "Μεταπώληση: χωρίς ΦΠΑ, ισχύουν τέλη μεταβίβασης",
      newbuild: "Νέα οικοδομή: επιβάλλεται ΦΠΑ, οπότε τα τέλη μεταβίβασης είναι μηδέν",
      vatPart: "ΦΠΑ",
      transferPart: "Τέλη μεταβίβασης",
      stampPart: "Χαρτόσημο",
      purchaseTotal: "Τα τρία μαζί",
      notFees: "Δικηγόρος, μεσίτης και τοπικά τέλη δεν περιλαμβάνονται.",
      incomeCmp: "Φορολογητέο εισόδημα, ή πορτογαλικό rendimento coletável (EUR)",
      profitCmp: "Κέρδος εταιρείας (EUR)",
      uaeBand: "Ποσό σε ευρώ της μηδενικής ζώνης ΗΑΕ (375.000 ντιρχάμ). Βάλτε 0 για 9% σε όλο το κέρδος.",
      otherRate: "Ενιαίος συντελεστής που δίνετε εσείς για άλλη χώρα (%). Βάλτε 0 για να παραλειφθεί.",
      cyPerson: "Φόρος εισοδήματος Κύπρου",
      ptPerson: "Φόρος εισοδήματος Πορτογαλίας, κλίμακα ηπειρωτικής χώρας 2026",
      uaePerson: "Φόρος εισοδήματος φυσικού προσώπου ΗΑΕ",
      otherPerson: "Φόρος με τον συντελεστή που πληκτρολογήσατε",
      cyCo: "Εταιρικός φόρος Κύπρου 15%",
      mtCo: "Εταιρικός φόρος Μάλτας 35%, χωρίς επιστροφή",
      ptCo: "Εταιρικός φόρος Πορτογαλίας 19%, ηπειρωτική χώρα",
      grCo: "Εταιρικός φόρος Ελλάδας 22%",
      uaeCo: "Εταιρικός φόρος ΗΑΕ",
      compareNote: "Οι προσωπικές κλίμακες της Μάλτας για το 2026 και η προσωπική κλίμακα της Ελλάδας δεν υπολογίζονται. Οι κοινωνικές ασφαλίσεις δεν περιλαμβάνονται.",
      consult: "Θέλετε ακριβή υπολογισμό για το ακίνητό σας; Ζητήστε δωρεάν συμβουλή"
    },
    ru: {
      value: "Принятая стоимость (EUR)",
      price: "Цена без НДС (EUR)",
      vatYes: "С этой покупки взимается НДС",
      vatNo: "НДС не взимается (обычная вторичная продажа)",
      forced: "Продавец приобрёл объект на принудительной продаже (части VI / VIA закона 9/1965). Скидка 50% не применяется.",
      late: "Договор не сдан в Земельный кадастр в течение шести месяцев (по буклету DLS сбор увеличивается на 10%).",
      buyers: "Покупателей с равными долями (сбор считается с доли каждого)",
      yearNew: "Хотя бы одна сторона подпишет 1 января 2026 или позже",
      yearOld: "Хотя бы одна сторона подписала не позднее 31 декабря 2025",
      area: "Площадь застройки (м²)",
      home: "Заявляется ставка 5% для основного и постоянного жилья",
      disability: "Заявитель с инвалидностью (5% на первые 190 м²; потолок общей площади 190 м² не применяется). Пределы стоимости всё равно учитываются. Право нужно подтвердить в Налоговом департаменте.",
      sale: "Выручка от продажи (EUR)",
      cost: "Стоимость приобретения и улучшений до индексации (EUR)",
      ratio: "Официальный коэффициент индексации (1 = без надбавки). Возьмите его из таблицы инфляции Налогового департамента. Не подставляйте наугад.",
      sellCosts: "Расходы на продажу без индексации (юрист, агент и т. п.) (EUR)",
      exNone: "Без пожизненного вычета (компания или вычет уже использован)",
      exGen: "Общий вычет для физического лица, €30 000",
      exAgri: "Сельхозземля, проданная фермером, €50 000",
      exHome: "Вычет для основного жилья, €150 000",
      used: "Вычет, уже использованный по прошлым сделкам (EUR)",
      rent: "Годовая валовая аренда (EUR)",
      otherInc: "Другой налогооблагаемый доход за год, без этой аренды (EUR)",
      extra: "Другие вычитаемые расходы по этой сдаче, без уставных 20% (EUR)",
      purchase: "Цена, уплаченная за объект (EUR)",
      principal: "Сумма кредита (EUR)",
      rate: "Годовая ставка (%)",
      years: "Срок (лет)",
      calc: "Рассчитать",
      result: "Результат",
      note: "Это иллюстрация, а не расчёт ведомства.",
      perBuyer: "На покупателя",
      fullScale: "Шкала до снижения",
      after: "После выбранного правила",
      band: "Диапазон",
      duty: "Гербовый сбор",
      zero: "Гербовый сбор по этому документу — €0.",
      vat5: "Сумма по ставке 5%",
      vat19: "Сумма по ставке 19%",
      vatTotal: "НДС",
      ineligible: "При таких цифрах ставка 5% недоступна. НДС — 19% со всей цены.",
      notClaimed: "Без заявления об основном жилье НДС — 19% со всей цены.",
      gain: "Прирост после индексации и расходов на продажу",
      exempt: "Вычет, применённый к этой продаже",
      taxable: "Облагаемый прирост",
      cgt: "Налог на прирост капитала по ставке 20%",
      grossYield: "Валовая доходность",
      deduction: "Уставный вычет 20%",
      rentalProfit: "Арендная сумма, включённая в подоходный налог",
      incomeTax: "Подоходный налог, вызванный этой суммой",
      ghs: "ГЕСИ 2,65% с валовой аренды (годовой потолок здесь не применяется)",
      sdc: "Сбор на оборону с этой аренды в 2026 году",
      netYield: "Доходность после этого подоходного налога и ГЕСИ",
      monthly: "Ежемесячный платёж",
      totalPay: "Всего за срок",
      interest: "Из них проценты",
      schedule: "Платёж рассчитан при фиксированной ставке и полном погашении, без комиссий банка.",
      salary: "Другой налогооблагаемый доход, кроме этих дивидендов и этих процентов (EUR)",
      dividend: "Дивиденды (EUR)",
      interestAmt: "Проценты (EUR)",
      profitNew: "Дивиденды из прибыли 2026 года (ставка для лица с домицилем 5%)",
      profitOld: "Дивиденды кипрской компании из прибыли по 2025 год, полученные до 31 декабря 2031 года (ставка для лица с домицилем 17%)",
      lowInc: "Весь доход ниже €12 000, поэтому проценты лица с домицилем — по 3%, а не по 17%",
      nondomCol: "Без домициля",
      domCol: "С домицилем",
      itax: "Подоходный налог с другого дохода",
      sdcDiv: "Взнос на оборону с дивидендов",
      sdcInt: "Взнос на оборону с процентов",
      totalTax: "Подоходный налог плюс эти два взноса",
      sameBands: "Шкалы подоходного налога от домициля не меняются.",
      profit: "Прибыль до этого сравнения (EUR)",
      shNon: "У акционера нет домициля",
      shDom: "У акционера есть домициль, и дивиденд из прибыли 2026 года",
      cit: "Корпоративный налог 15%",
      afterCit: "Выплачивается дивидендом после этого корпоративного налога",
      coTotal: "Путь компании",
      seTax: "Путь самозанятого, только подоходный налог",
      notSi: "Социальное страхование, ГЕСИ и расходы ни в одну цифру не входят.",
      resale: "Вторичная продажа: без НДС, сборы за переход есть",
      newbuild: "Новостройка: НДС взимается, поэтому сборы за переход равны нулю",
      vatPart: "НДС",
      transferPart: "Сборы за переход",
      stampPart: "Гербовый сбор",
      purchaseTotal: "Эти три вместе",
      notFees: "Юрист, агент и местные сборы не включены.",
      incomeCmp: "Налогооблагаемый доход или португальский rendimento coletável (EUR)",
      profitCmp: "Прибыль компании (EUR)",
      uaeBand: "Сумма в евро нулевой полосы ОАЭ (375 000 дирхамов). Поставьте 0, чтобы взять 9% со всей прибыли.",
      otherRate: "Плоская ставка, которую вы задаёте для другой страны (%). Поставьте 0, чтобы пропустить.",
      cyPerson: "Подоходный налог Кипра",
      ptPerson: "Подоходный налог Португалии, шкала материка 2026 года",
      uaePerson: "Подоходный налог физического лица в ОАЭ",
      otherPerson: "Налог по ставке, которую вы ввели",
      cyCo: "Корпоративный налог Кипра 15%",
      mtCo: "Корпоративный налог Мальты 35%, без возврата",
      ptCo: "Корпоративный налог Португалии 19%, материк",
      grCo: "Корпоративный налог Греции 22%",
      uaeCo: "Корпоративный налог ОАЭ",
      compareNote: "Личные шкалы Мальты на 2026 год и личная шкала Греции не считаются. Социальное страхование не включено.",
      consult: "Нужен точный расчёт по вашему объекту? Получите бесплатную консультацию"
    }
  }[lang];

  function money(n) {
    if (!isFinite(n)) return "—";
    var neg = n < 0;
    n = Math.abs(n);
    var s = n.toFixed(2);
    var parts = s.split(".");
    var sep = lang === "en" ? "," : (lang === "el" ? "." : " ");
    var dec = lang === "en" ? "." : ",";
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, sep);
    var body = parts[0] + dec + parts[1];
    return (neg ? "−" : "") + "€" + body;
  }
  function num(id) {
    var el = document.getElementById(id);
    var v = parseFloat(String(el.value).replace(/\s/g, "").replace(",", "."));
    return isFinite(v) ? v : 0;
  }
  function qnum(names) {
    var params = new URLSearchParams(location.search);
    for (var i = 0; i < names.length; i++) {
      var raw = params.get(names[i]);
      if (raw == null || String(raw).trim() === "") continue;
      var v = parseFloat(String(raw).replace(/\s/g, "").replace(",", "."));
      if (isFinite(v) && v >= 0) return String(v);
    }
    return null;
  }
  function field(id, label, value, step) {
    return '<label class="fld" for="' + id + '"><span>' + label + '</span><input id="' + id + '" inputmode="decimal" step="' + (step || "0.01") + '" value="' + value + '"></label>';
  }
  function check(id, label, on) {
    return '<label class="chk"><input type="checkbox" id="' + id + '"' + (on ? " checked" : "") + '><span>' + label + "</span></label>";
  }
  function radio(name, id, label, on) {
    return '<label class="chk"><input type="radio" name="' + name + '" id="' + id + '"' + (on ? " checked" : "") + '><span>' + label + "</span></label>";
  }
  function rows(list) {
    return '<table class="out"><tbody>' + list.map(function (r) {
      return "<tr><th>" + r[0] + "</th><td>" + r[1] + "</td></tr>";
    }).join("") + "</tbody></table>";
  }
  function transferScale(v) {
    var a = Math.min(v, 85000);
    var b = Math.min(Math.max(v - 85000, 0), 85000);
    var c = Math.max(v - 170000, 0);
    return [
      { label: "€0.01 – €85,000 × 3%", amount: a * 0.03 },
      { label: "€85,001 – €170,000 × 5%", amount: b * 0.05 },
      { label: "€170,001+ × 8%", amount: c * 0.08 }
    ];
  }
  function incomeTax(income) {
    if (income <= 0) return 0;
    var bands = [[22000, 0], [10000, 0.20], [10000, 0.25], [30000, 0.30]];
    var left = income, tax = 0;
    for (var i = 0; i < bands.length; i++) {
      var take = Math.min(left, bands[i][0]);
      tax += take * bands[i][1];
      left -= take;
      if (left <= 0) return tax;
    }
    return tax + left * 0.35;
  }
  function stampOld(v) {
    if (v <= 5000) return 0;
    var duty = 0;
    var mid = Math.min(v, 170000) - 5000;
    if (mid > 0) duty += Math.ceil(mid / 1000) * 1.5;
    if (v > 170000) duty += Math.ceil((v - 170000) / 1000) * 2;
    return Math.min(duty, 20000);
  }
  function sliceTax(income, cuts) {
    if (income <= 0) return 0;
    var prev = 0, tax = 0;
    for (var i = 0; i < cuts.length; i++) {
      var cap = Math.min(income, cuts[i][0]);
      if (cap > prev) tax += (cap - prev) * cuts[i][1];
      prev = cuts[i][0];
      if (income <= cuts[i][0]) break;
    }
    return tax;
  }
  var PORTUGAL = [[8342, 0.122], [12587, 0.152], [17838, 0.207], [23089, 0.236], [29397, 0.306], [43090, 0.346], [46566, 0.431], [86634, 0.446], [Infinity, 0.48]];
  function vatOn(price, area, home, disability) {
    var capM = disability ? 190 : 130;
    var maxM = disability ? Infinity : 190;
    var eligible = home && area > 0 && area <= maxM && price <= 475000;
    if (!eligible) return price * 0.19;
    var portion = price * (Math.min(capM, area) / area) * (Math.min(350000, price) / price);
    return portion * 0.05 + Math.max(0, price - portion) * 0.19;
  }

  var forms = {
    transfer: function () {
      return field("value", T.value, qnum(["value", "price"]) || "200000") +
        radio("vat", "vatNo", T.vatNo, true) + radio("vat", "vatYes", T.vatYes, false) +
        check("forced", T.forced, false) + check("late", T.late, false) +
        field("buyers", T.buyers, "1", "1");
    },
    stamp: function () {
      return field("value", T.value, qnum(["value", "price"]) || "300000") +
        radio("when", "yearNew", T.yearNew, true) + radio("when", "yearOld", T.yearOld, false);
    },
    vat: function () {
      return field("price", T.price, qnum(["price"]) || "300000") + field("area", T.area, qnum(["area"]) || "120", "0.1") +
        check("home", T.home, true) + check("disability", T.disability, false);
    },
    cgt: function () {
      return field("sale", T.sale, "300000") + field("cost", T.cost, "180000") +
        field("ratio", T.ratio, "1", "0.0001") + field("sellCosts", T.sellCosts, "0") +
        '<fieldset class="choices"><legend>' + T.exempt + "</legend>" +
        radio("ex", "exGen", T.exGen, true) + radio("ex", "exHome", T.exHome, false) +
        radio("ex", "exAgri", T.exAgri, false) + radio("ex", "exNone", T.exNone, false) +
        "</fieldset>" + field("used", T.used, "0");
    },
    rental: function () {
      return field("purchase", T.purchase, "250000") + field("rent", T.rent, "12000") +
        field("otherInc", T.otherInc, "0") + field("extra", T.extra, "0");
    },
    mortgage: function () {
      return field("principal", T.principal, qnum(["principal", "price"]) || "200000") + field("rate", T.rate, "4", "0.01") +
        field("years", T.years, "20", "1");
    },
    nondom: function () {
      return field("salary", T.salary, "40000") + field("dividend", T.dividend, "20000") + field("interestAmt", T.interestAmt, "0") +
        radio("profits", "profitNew", T.profitNew, true) + radio("profits", "profitOld", T.profitOld, false) +
        check("lowInc", T.lowInc, false);
    },
    company: function () {
      return field("profit", T.profit, "80000") +
        radio("shareholder", "shNon", T.shNon, true) + radio("shareholder", "shDom", T.shDom, false);
    },
    purchase: function () {
      return field("price", T.price, qnum(["price", "value"]) || "300000") + field("area", T.area, qnum(["area"]) || "120", "0.1") +
        radio("kindp", "resale", T.resale, true) + radio("kindp", "newbuild", T.newbuild, false) +
        check("home", T.home, true) + check("disability", T.disability, false) +
        field("buyers", T.buyers, "1", "1") + check("forced", T.forced, false) + check("late", T.late, false) +
        radio("when", "yearNew", T.yearNew, true) + radio("when", "yearOld", T.yearOld, false);
    },
    compare: function () {
      return field("incomeCmp", T.incomeCmp, "60000") + field("profitCmp", T.profitCmp, "80000") +
        field("uaeBand", T.uaeBand, "0") + field("otherRate", T.otherRate, "0", "0.01");
    }
  };

  function run() {
    var box = document.getElementById("result");
    var list = [];
    if (kind === "transfer") {
      var buyers = Math.max(1, Math.round(num("buyers")));
      var share = Math.max(0, num("value")) / buyers;
      var bands = transferScale(share);
      var full = bands.reduce(function (s, b) { return s + b.amount; }, 0);
      var vatCharged = document.getElementById("vatYes").checked;
      var forced = document.getElementById("forced").checked;
      var fee = vatCharged ? 0 : (forced ? full : full * 0.5);
      if (document.getElementById("late").checked) fee *= 1.1;
      bands.forEach(function (b) { list.push([b.label, money(b.amount)]); });
      list.push([T.fullScale + " (" + T.perBuyer + ")", money(full)]);
      list.push([T.after + " (" + T.perBuyer + ")", money(fee)]);
      list.push([T.after + " × " + buyers, money(fee * buyers)]);
    } else if (kind === "stamp") {
      if (document.getElementById("yearNew").checked) {
        list.push([T.duty, money(0)]);
        list.push(["", T.zero]);
      } else {
        list.push([T.duty, money(stampOld(Math.max(0, num("value"))))]);
      }
    } else if (kind === "vat") {
      var price = Math.max(0, num("price"));
      var area = Math.max(0, num("area"));
      var home = document.getElementById("home").checked;
      var disability = document.getElementById("disability").checked;
      var capM = disability ? 190 : 130;
      var maxM = disability ? Infinity : 190;
      var eligible = home && area > 0 && area <= maxM && price <= 475000;
      var at5 = 0, at19 = price, why = "";
      if (!home) why = T.notClaimed;
      else if (!eligible) why = T.ineligible;
      else {
        var portion = price * (Math.min(capM, area) / area) * (Math.min(350000, price) / price);
        at5 = portion;
        at19 = Math.max(0, price - portion);
        why = "";
      }
      if (!eligible) { at5 = 0; at19 = price; }
      list.push([T.vat5, money(at5)]);
      list.push([T.vat19, money(at19)]);
      list.push([T.vatTotal, money(at5 * 0.05 + at19 * 0.19)]);
      if (why) list.push(["", why]);
    } else if (kind === "cgt") {
      var indexed = Math.max(0, num("cost")) * Math.max(0, num("ratio"));
      var gain = num("sale") - indexed - Math.max(0, num("sellCosts"));
      var cap = document.getElementById("exHome").checked ? 150000 :
        document.getElementById("exAgri").checked ? 50000 :
        document.getElementById("exGen").checked ? 30000 : 0;
      var allowance = Math.max(0, cap - Math.max(0, num("used")));
      var applied = Math.min(Math.max(gain, 0), allowance);
      var taxable = Math.max(0, gain - applied);
      list.push([T.gain, money(gain)]);
      list.push([T.exempt, money(applied)]);
      list.push([T.taxable, money(taxable)]);
      list.push([T.cgt, money(taxable * 0.2)]);
    } else if (kind === "rental") {
      var gross = Math.max(0, num("rent"));
      var ded = gross * 0.2;
      var profit = Math.max(0, gross - ded - Math.max(0, num("extra")));
      var other = Math.max(0, num("otherInc"));
      var tax = incomeTax(other + profit) - incomeTax(other);
      var ghs = gross * 0.0265;
      var pricePaid = Math.max(0, num("purchase"));
      list.push([T.deduction, money(ded)]);
      list.push([T.rentalProfit, money(profit)]);
      list.push([T.incomeTax, money(tax)]);
      list.push([T.ghs, money(ghs)]);
      list.push([T.sdc, money(0)]);
      if (pricePaid > 0) {
        list.push([T.grossYield, (gross / pricePaid * 100).toFixed(2) + "%"]);
        list.push([T.netYield, ((gross - tax - ghs) / pricePaid * 100).toFixed(2) + "%"]);
      }
    } else if (kind === "mortgage") {
      var P = Math.max(0, num("principal"));
      var annual = Math.max(0, num("rate")) / 100;
      var years = Math.max(0, num("years"));
      var n = Math.round(years * 12);
      var pay = 0;
      if (n > 0) {
        var r = annual / 12;
        pay = r === 0 ? P / n : P * r * Math.pow(1 + r, n) / (Math.pow(1 + r, n) - 1);
      }
      list.push([T.monthly, money(pay)]);
      list.push([T.totalPay, money(pay * n)]);
      list.push([T.interest, money(pay * n - P)]);
      list.push(["", T.schedule]);
    } else if (kind === "nondom") {
      var other = Math.max(0, num("salary"));
      var div = Math.max(0, num("dividend"));
      var intr = Math.max(0, num("interestAmt"));
      var tax = incomeTax(other);
      var divRate = document.getElementById("profitOld").checked ? 0.17 : 0.05;
      var intRate = document.getElementById("lowInc").checked ? 0.03 : 0.17;
      list.push([T.itax + " — " + T.nondomCol, money(tax)]);
      list.push([T.itax + " — " + T.domCol, money(tax)]);
      list.push([T.sdcDiv + " — " + T.nondomCol, money(0)]);
      list.push([T.sdcDiv + " — " + T.domCol, money(div * divRate)]);
      list.push([T.sdcInt + " — " + T.nondomCol, money(0)]);
      list.push([T.sdcInt + " — " + T.domCol, money(intr * intRate)]);
      list.push([T.totalTax + " — " + T.nondomCol, money(tax)]);
      list.push([T.totalTax + " — " + T.domCol, money(tax + div * divRate + intr * intRate)]);
      list.push(["", T.sameBands]);
    } else if (kind === "company") {
      var profit = Math.max(0, num("profit"));
      var cit = profit * 0.15;
      var left = Math.max(0, profit - cit);
      var sdc = document.getElementById("shDom").checked ? left * 0.05 : 0;
      list.push([T.cit, money(cit)]);
      list.push([T.afterCit, money(left)]);
      list.push([T.sdcDiv, money(sdc)]);
      list.push([T.coTotal, money(cit + sdc)]);
      list.push([T.seTax, money(incomeTax(profit))]);
      list.push(["", T.notSi]);
    } else if (kind === "purchase") {
      var priceP = Math.max(0, num("price"));
      var buyersP = Math.max(1, Math.round(num("buyers")));
      var shareP = priceP / buyersP;
      var fullP = transferScale(shareP).reduce(function (s, b) { return s + b.amount; }, 0);
      var transferP = 0;
      var vatP = 0;
      if (document.getElementById("newbuild").checked) {
        vatP = vatOn(priceP, Math.max(0, num("area")), document.getElementById("home").checked, document.getElementById("disability").checked);
      } else {
        transferP = document.getElementById("forced").checked ? fullP : fullP * 0.5;
        if (document.getElementById("late").checked) transferP *= 1.1;
        transferP *= buyersP;
      }
      var stampP = document.getElementById("yearNew").checked ? 0 : stampOld(priceP);
      list.push([T.vatPart, money(vatP)]);
      list.push([T.transferPart, money(transferP)]);
      list.push([T.stampPart, money(stampP)]);
      list.push([T.purchaseTotal, money(vatP + transferP + stampP)]);
      list.push(["", T.notFees]);
    } else if (kind === "compare") {
      var inc = Math.max(0, num("incomeCmp"));
      var prof = Math.max(0, num("profitCmp"));
      var band = Math.max(0, num("uaeBand"));
      var typed = Math.max(0, num("otherRate")) / 100;
      var uaeCorp = band <= 0 ? prof * 0.09 : Math.max(0, prof - band) * 0.09;
      list.push([T.cyPerson, money(incomeTax(inc))]);
      list.push([T.ptPerson, money(sliceTax(inc, PORTUGAL))]);
      list.push([T.uaePerson, money(0)]);
      if (typed > 0) list.push([T.otherPerson, money(inc * typed)]);
      list.push([T.cyCo, money(prof * 0.15)]);
      list.push([T.mtCo, money(prof * 0.35)]);
      list.push([T.ptCo, money(prof * 0.19)]);
      list.push([T.grCo, money(prof * 0.22)]);
      list.push([T.uaeCo, money(uaeCorp)]);
      list.push(["", T.compareNote]);
    }
    var consult = root.getAttribute("data-consult");
    var line = consult ? '<p class="consult"><a href="' + consult + '">' + T.consult + "</a></p>" : "";
    box.innerHTML = "<h2>" + T.result + "</h2>" + rows(list) + '<p class="fine">' + T.note + "</p>" + line;
  }

  root.innerHTML = '<form class="calcform" id="calcform">' + forms[kind]() +
    '<button class="go" type="submit">' + T.calc + "</button></form><div id=\"result\" class=\"result\" aria-live=\"polite\"></div>";
  document.getElementById("calcform").addEventListener("submit", function (e) {
    e.preventDefault();
    run();
  });
  run();
})();
