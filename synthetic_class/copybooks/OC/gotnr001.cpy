******************************************************************
*  COPYBOOK  : GOTNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : TN
******************************************************************
 01  RT-OTN-RATING.

          03 RT-OTN-TERRITORY-CODE            PIC X(3).
          03 RT-OTN-CLASS-CODE                PIC X(4).
          03 RT-OTN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OTN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OTN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OTN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OTN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OTN-RATED-PREMIUM             PIC 9(9)V9(2).
